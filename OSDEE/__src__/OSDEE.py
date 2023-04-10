import pandapower as pp
import networkx as nx
from pandapower import topology
import pandas as pd
import os
from datetime import datetime


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
        self._ms = _ms(self, float(self._param['variacao_ms'])/100, int(
            self._param['quantidade_csq'])//2)
        self._vns = _vns(self)
        self._qtd_gd = int(self._param['quantidade_gd'])
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
        df['closed'] = df['element'].isin(lines_disconnected) == False
        return net

    def set_gd_in_buses(self, net) -> pp.pandapowerNet:
        pp.runpp(net)
        for _ in range(self._qtd_gd):
            min_pu_bus = net.res_bus.vm_pu.idxmin()
            net.gen[net.gen.bus == min_pu_bus].in_service = True
            pp.runopp(net, init='pf')
        return net

    def run_vns_in_ms_systems(self, net, ms_group: set[tuple[int]]):
        saved = {
            'MS': [],
            'MS_loss': [],
            'VNS': [],
            'VNS_loss': []
        }
        for ms_instance in ms_group:
            net = self._set_net_from_id(net, ms_instance)
            net = self.set_gd_in_buses(net)
            net = self.vns.run(net, OSDEE.get_graph_from_net(net))
            saved['MS'].append(ms_instance)
            saved['MS_loss'].append(ms_group[ms_instance])
            saved['VNS'].append(OSDEE.get_network_id(net))
            saved['VNS_loss'].append(self.losses(net))
        return pd.DataFrame(saved)

    def _get_results_path(self, net: pp.pandapowerNet, minLoss: float) -> str:
        path = './resultados/'
        path += 'iwp' + self._param['initial_weight_prim'] + '_msv' + \
                self._param['quantidade_csq'] + '_gdq' + \
                self._param['quantidade_gd'] + '/'
        path += str(len(net.bus)) + '/'
        path += 'minLoss-' + str(int(minLoss*1e6)) + '/'
        path += datetime.now().isoformat(timespec='seconds').replace(':', '-')
        return path

    def save_results(self, net: pp.pandapowerNet, results: pd.DataFrame):
        path = self._get_results_path(net, min(results['VNS_loss']))
        os.makedirs(path, exist_ok=True)
        current_dir = os.getcwd()
        os.chdir(path)
        for index, row in results.iterrows():
            path_to_save = str(int(row['VNS_loss']*1e6)) + '/' + str(index+1)
            os.makedirs(path_to_save, exist_ok=True)
            self._save_result_in_path(path_to_save + '/ms', net, row['MS'])
            self._save_result_in_path(
                path_to_save + '/vns', net, row['VNS'])
        os.chdir(current_dir)

    def _save_result_in_path(self, path: str, net: pp.pandapowerNet, id: tuple[int]):
        os.makedirs(path)
        net = self._set_net_from_id(net, id)
        self.run_power_flow(net)
        net.res_bus.to_csv(path + '/barras.csv', sep=';', decimal=',')
        net.res_line.to_csv(path + '/linhas.csv', sep=';', decimal=',')
        net.res_gen.to_csv(path + '/gd.csv', sep=';', decimal=',')

    @staticmethod
    def get_graph_from_net(net: pp.pandapowerNet) -> nx.MultiGraph:
        graph = topology.create_nxgraph(net, multi=False)
        return graph
