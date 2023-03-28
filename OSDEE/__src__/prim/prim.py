import pandapower as pp
import networkx as nx
import pandas as pd
import pandapower.topology as topology
from ..OSDEE import OSDEE

class _prim:
    def __init__(self, base: OSDEE, initial_weight: int = 20, attribute: str = 'p_from_mw', ascending=False) -> None:
        self._base = base
        power_flow = self._get_lines_att(self._base.net, attribute)
        power_flow.sort_values(attribute, key = abs, ascending=ascending, inplace=True)
        self._base_graph: nx.Graph = topology.create_nxgraph(self._base.net, multi=False, respect_switches=False)
        i = initial_weight
        for index_line, data_line in power_flow.iterrows():
            de = data_line['from_bus']
            para = data_line['to_bus']
            if index_line in self._base.net['switch']['element'].values:
                self._base_graph[de][para]['weight']=i
            else:
                self._base_graph[de][para]['weight']=0
            i+=1
    
    def mst(self) -> nx.MultiGraph:
        return nx.algorithms.minimum_spanning_tree(self._base_graph, algorithm='prim')

    def _get_line_power_flow(self, grid: pp.pandapowerNet) -> pd.DataFrame:
        self._base.run_power_flow(grid)
        power_flow: pd.Series = grid.get('res_line')['p_from_mw']
        return power_flow

    def _get_line_resistence(self, grid: pp.pandapowerNet) -> pd.DataFrame:
        lines = grid.get('line')
        resistence = lines['length_km']*lines['r_ohm_per_km']
        return resistence

    def _get_lines_att(self, grid: pp.pandapowerNet, att: str) -> pd.DataFrame:
        func = _prim._implemented_get_lines_att.get(att)
        if func == None:
            raise Exception(f'Get {att} from grid was not implemented yet')
        ret = func(self, grid)
        lines = grid.get('line')[['from_bus', 'to_bus']]
        ret = pd.concat([lines,ret], axis=1)
        return ret
    
_prim._implemented_get_lines_att = {
    'p_from_mw': _prim._get_line_power_flow,
    'resistance': _prim._get_line_resistence
}