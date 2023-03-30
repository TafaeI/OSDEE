import networkx as nx
import pandapower as pp
import copy
import random
import sys
from tqdm import trange
from ... import OSDEE

class _ms:
    def __init__(self, base: OSDEE, range: float = .4, len_best: int = 5) -> None:
        self._base = base
        self._graph = base.prim._base_graph
        self._var_graph = copy.deepcopy(self._graph)
        self._range = range
        self.saved_networks = dict()
        self._len_best = len_best
        pass

    def get_ms(self) -> nx.MultiGraph:
        for bfrom, bto in self._var_graph.edges():
            variation_multiplier = 1 + self._range*(1-random.random())
            self._var_graph[bfrom][bto]['weight'] = variation_multiplier*self._graph[bfrom][bto]['weight']
        return self._var_graph
    
    def _run_and_save(self) -> tuple[tuple[int], float]:
        graph = self._base.prim.mst(self.get_ms())
        net = OSDEE.set_net_from_graph(self._base.net, graph)
        net_id = OSDEE.get_network_id(net)
        if net_id not in self.saved_networks:
            losses = self._base.losses(net)
            self.saved_networks[net_id] = losses
            return net_id, losses
        return None, None
    
    @staticmethod
    def _get_minimum_losses(group_qtd: int, _to: dict, _from: dict) -> dict:
        for _ in range(group_qtd):
            net_id = min(_from, key=_from.get)
            _to[net_id] = _from.pop(net_id)
        return _to
    
    @staticmethod
    def _get_min_diff(_to: dict[tuple[int], float], from_net: tuple[int]) -> int:
        min = sys.maxsize
        for to_net in _to:
            dif = len(set(to_net) - set(from_net))
            if dif<min:
                min = dif
        return min

    @staticmethod
    def _get_max_diff(_to: dict[tuple[int], float], _from: dict[tuple[int], float]) -> tuple[int]:
        max = -1
        ret = None
        for from_net in _from:
            dif = _ms._get_min_diff(_to, from_net)
            if dif>max:
                max = dif
                ret = from_net
        return ret

    @staticmethod
    def _get_max_min_diff(group_qtd: int, _to: dict[tuple[int], float], _from: dict[tuple[int], float]) -> dict[tuple[int], float]:
        for _ in range(group_qtd):
            net_id = _ms._get_max_diff(_to, _from)
            if net_id == None: return _to
            _to[net_id] = _from.pop(net_id)
        return _to
                

    def run(self, iters: int) -> dict[tuple[int], float]:
        for _ in trange(iters, desc='Multi-Start'):
            self._run_and_save()
        saved = copy.deepcopy(self.saved_networks)
        self.best_group = dict()
        self.best_group = self._get_minimum_losses(self._len_best, self.best_group, saved)
        self.best_group = self._get_max_min_diff(self._len_best, self.best_group, saved)
        return self.best_group