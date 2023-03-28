import pandapower as pp
import networkx as nx
import pandas as pd

class OSDEE:
    def __init__(self, net: pp.pandapowerNet) -> None:
        from .prim import _prim
        from .ms import _ms
        from .vns import _vns
        self.net = net
        self._switches = OSDEE._get_all_switches(net)
        self._power_flow_method = pp.runpp
        self._prim = _prim(self)
        self._ms = _ms(self)
        self._vns = _vns(self)
        pass

    @property
    def prim(self):
        return self._prim

    @property
    def ms(self):
        return self._ms

    @property
    def vns(self):
        return self._vns

    @staticmethod
    def set_net_from_graph(net: pp.pandapowerNet, graph: nx.MultiGraph) -> pp.pandapowerNet:
        lines = set(line[1] for _, _, line in graph.edges(data='key'))
        df = net['switch']
        df['closed'] = df['element'].isin(lines)
        return net

    @staticmethod
    def _get_gen_buses(net: pp.pandapowerNet) -> tuple[int]:
        gen_buses = [g[1].bus for g in net['gen'].iterrows()]
        gen_buses.sort()
        length = len(gen_buses)
        ret = (length,) + tuple(gen_buses)
        return ret
    
    @staticmethod
    def _get_lines_disconnected(net: pp.pandapowerNet) -> tuple[int]:
        switch = net['switch']
        open_switch = switch[switch['closed']==False]
        lines = set(open_switch['element'].values)
        return tuple(sorted(lines))

    @staticmethod
    def get_network_id(network: pp.pandapowerNet) -> tuple[int]:
        gen_buses = OSDEE._get_gen_buses(network)
        disc_lines = OSDEE._get_lines_disconnected(network)
        ret = gen_buses + disc_lines
        return ret

    @staticmethod
    def _get_all_switches(net: pp.pandapowerNet) -> set[tuple[int, int]]:
        switches = set()
        for line in net['switch']['element'].unique():
            u = net['line']['from_bus'][line]
            v = net['line']['to_bus'][line]
            switches.add((u,v))
            switches.add((v,u))
        return switches
    
    @staticmethod
    def _get_substation_bus(net: pp.pandapowerNet) -> int:
        return net.ext_grid.bus[0]

    @staticmethod
    def _get_all_buses(net: pp.pandapowerNet) -> set[int]:
        ret = set(net.bus.index)
        return ret
    
    @staticmethod
    def _set_opf_cost_function(net: pp.pandapowerNet) -> None:
        pp.create_poly_cost(net, 0, 'ext_grid', cp1_eur_per_mw=1)
        pp.create_poly_costs(net, net.gen.index, 'gen', cp1_eur_per_mw=1)

    @staticmethod
    def _get_sum_load(net: pp.pandapowerNet) -> None:
        return sum(net.load.p_mw)

    def has_switch(self, edge: tuple[int, int]) -> bool:
        return edge in self._switches    

    def set_power_flow(self, func: callable) -> None:
        self._power_flow_method = func
    
    def run_power_flow(self, net: pp.pandapowerNet) -> None:
        self._power_flow_method(net)

    def losses(self, net: pp.pandapowerNet) -> float:
        self.run_power_flow(net)
        return -sum(net['res_bus']['p_mw'])