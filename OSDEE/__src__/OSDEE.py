import pandapower as pp
import networkx as nx
import pandas as pd


class OSDEE:
    def __init__(self, net: int | pp.pandapowerNet) -> None:
        from .prim import _prim
        from .ms import _ms
        from .vns import _vns
        from .load import load_system, get_parameters_config
        if not isinstance(net, pp.pandapowerNet):
            net = load_system(net)
        self._param = get_parameters_config()
        self.net = net
        self._switches = OSDEE._get_all_switches(net)
        self._power_flow_method = pp.runpp
        self._prim = _prim(self, int(
            self._param['initial_weight_prim']), self._param['attribute_weight_prim'])
        self._ms = _ms(self, float(self._param['variacao_ms']), int(
            self._param['quantidade_csq'])//2)
        self._vns = _vns(self)
        self._qtd_gd = self._param['quantidade_gd']
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
        gen_buses = list(net.gen[net.gen.in_service == True].bus)
        gen_buses.sort()
        length = len(gen_buses)
        ret = (length,) + tuple(gen_buses)
        return ret

    @staticmethod
    def _get_lines_disconnected(net: pp.pandapowerNet) -> tuple[int]:
        switch = net['switch']
        open_switch = switch[switch['closed'] == False]
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
            switches.add((u, v))
            switches.add((v, u))
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

    def _set_net_from_id(self, net: pp.pandapowerNet, id: tuple[int]) -> pp.pandapowerNet:
        qtd_gd = id[0]
        id = id[1:]
        bus_gd = id[:qtd_gd]
        lines_disconnected = id[qtd_gd:]
        net.gen.in_service = net.gen.bus.isin(bus_gd)
        df = net['switch']
        df['closed'] = df['element'].isin(lines_disconnected)==False
        return net

    def set_gd_in_buses(self, net) -> pp.pandapowerNet:
        pp.runpp(net)
        for _ in range(self._qtd_gd):
            min_pu_bus = net.res_bus.vm_pu.idxmin()
            net.gen[net.gen.bus == min_pu_bus].in_service = True
            pp.runopp(net, init='pf')