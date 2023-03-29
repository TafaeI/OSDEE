import networkx as nx
import pandapower as pp
import logging
from ... import OSDEE

class _vns:
    def __init__(self, base: OSDEE) -> None:
        self._base = base
        pass

    @staticmethod
    def get_edges_to_add(full_graph: nx.MultiGraph, curr_graph: nx.MultiGraph) -> list:
        edges = (full_graph.edges - curr_graph.edges)
        ret = [{'u_of_edge':u, 'v_of_edge':v, **full_graph[u][v]} for u,v in edges]
        return ret

    @staticmethod
    def get_cycles(graph: nx.MultiGraph):
        return nx.chain_decomposition(graph)

    def get_best_remove_edge(self, net: pp.pandapowerNet, graph: nx.MultiGraph):
        loss_best = float('inf')
        edge_best = None
        removable_edges = tuple(next(_vns.get_cycles(graph)))
        for edge in removable_edges:
            if self._base.has_switch(edge):
                edge_data = graph[edge[0]][edge[1]]
                graph.remove_edge(*edge)
                logging.info(f'Removed edge {edge[0]} - {edge[1]}')
                try:
                    loss = self._base.losses(self._base.set_net_from_graph(net, graph))
                except pp.LoadflowNotConverged:
                    logging.error('\t-> Não convergiu')
                    loss = float('inf')
                graph.add_edge(*edge, **edge_data)
                if loss<loss_best:
                    loss_best = loss
                    edge_best = edge
        return edge_best

    def vns_in_lines(self, net: pp.pandapowerNet, current_graph: nx.MultiGraph) -> nx.MultiGraph:
        fim = False
        while not fim:
            fim = True
            for edge in _vns.get_edges_to_add(self._base.prim._base_graph, current_graph):
                current_graph.add_edge(**edge)
                logging.info(f"Added edge {edge['u_of_edge']} - {edge['v_of_edge']}")
                best_to_remove = self.get_best_remove_edge(net, current_graph)
                current_graph.remove_edge(*best_to_remove)
                if set(best_to_remove)!=set((edge['u_of_edge'],edge['v_of_edge'])):
                    fim = False
        return current_graph

    def set_best_bus_gd(self, net: pp.pandapowerNet, possible_buses: list[int]) -> int:
        loss_best = float('inf')
        for bus in possible_buses:
            logging.info(f'Trying bus {bus}')
            net.gen.in_service[net.gen.bus == bus] = True
            try:
                loss = self._base.losses(net)
            except pp.OPFNotConverged:
                logging.error('\t -> Não convergiu')
                loss = float('inf')
            net.gen.in_service[net.gen.bus == bus] = False
            if loss < loss_best:
                loss_best = loss
                bus_best = bus
        net.gen.in_service[net.gen.bus == bus_best] = True
        return bus_best

    def vns_in_gd(self, net: pp.pandapowerNet) -> pp.pandapowerNet:
        fim = False
        while not fim:
            fim = True
            gen_buses = set(net.gen.bus[net.gen.in_service==True])
            possible_buses = self._base._get_all_buses(net)
            possible_buses.remove(self._base._get_substation_bus(net))
            possible_buses-= gen_buses
            possible_buses = list(possible_buses)
            for bus in gen_buses:
                net.gen.in_service[net.gen.bus==bus] = False
                possible_buses.append(bus)
                logging.info(f'Trying to replace gd in bus {bus}')
                best_bus = self.set_best_bus_gd(net, possible_buses)
                possible_buses.remove(best_bus)
                if best_bus != bus:
                    fim = False
        return net
    
    def run(self, net: pp.pandapowerNet, graph: nx.MultiGraph) -> pp.pandapowerNet:
        graph = self.vns_in_lines(net, graph)
        net = OSDEE.set_net_from_graph(net, graph)
        return self.vns_in_gd(net)

if __name__=='__main__':
    pass