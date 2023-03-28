from OSDEE import OSDEE
import warnings
import pandapower as pp
from pandapower import topology
from pandapower import plotting
from networkx.drawing import nx_pylab
from matplotlib import pyplot as plt
import networkx as nx
import pandas as pd
import logging
import timeit
from sys import stdout

def create_line_with_switch(net, bus1, bus2, km, type):
    line = pp.create_line(net, bus1, bus2, km, type)
    pp.create_switch(net, bus1, line, 'l')
    pp.create_switch(net, bus2, line, 'l')
    

def create_test_system() -> pp.pandapowerNet:
    slack = 0
    net = pp.create_empty_network('default', 60, 100e3)
    for _ in range(6):
        bus = pp.create_bus(net, 13.8, max_vm_pu=1.05, min_vm_pu=0.95)
        if bus!=slack:
            pp.create_gen(net, bus, 0, min_p_mw=-10, max_p_mw=10, min_q_mvar=-5, max_q_mvar=5, in_service=False)
    create_line_with_switch(net,0,1,1,"NA2XS2Y 1x95 RM/25 12/20 kV")
    create_line_with_switch(net,0,2,2,"NA2XS2Y 1x95 RM/25 12/20 kV")
    create_line_with_switch(net,1,2,1,"NA2XS2Y 1x95 RM/25 12/20 kV")
    create_line_with_switch(net,1,3,3,"NA2XS2Y 1x95 RM/25 12/20 kV")
    create_line_with_switch(net,1,4,4,"NA2XS2Y 1x95 RM/25 12/20 kV")
    create_line_with_switch(net,2,4,2,"NA2XS2Y 1x95 RM/25 12/20 kV")
    create_line_with_switch(net,3,4,1,"NA2XS2Y 1x95 RM/25 12/20 kV")
    create_line_with_switch(net,3,5,2,"NA2XS2Y 1x95 RM/25 12/20 kV")
    create_line_with_switch(net,4,5,2,"NA2XS2Y 1x95 RM/25 12/20 kV")
    net.gen.in_service[net.gen.bus == 4] = True
    pp.create_ext_grid(net, slack)
    pp.create_load(net,5,5)
    return net

if __name__=='__main__':
    warnings.filterwarnings("ignore",category=FutureWarning)
    logging.basicConfig(
        stream=stdout,
        level=logging.INFO
    )
    net = create_test_system()
    sys = OSDEE(net)
    sys._set_opf_cost_function(sys.net)
    sys.set_power_flow(lambda x: pp.runopp(x))
    # print(sys.net.poly_cost)
    graph = sys.prim.mst(sys.prim._base_graph)
    print(sys.losses(sys.set_net_from_graph(sys.net, graph)))
    net = sys.vns.run(sys.net, graph)
    print(sys.losses(net))
    print(net.res_gen)
    # sys.vns.vns_in_gd(sys.net)
# Gprim.remove_edge(9,19)
# connectedNodes = nx.components.connected_components(Gprim)
# c1, c2 = connectedNodes
# edges = []
# for node in c1:
#     possib = set(Gcomplete[node]) - c1
#     edges += [(node, neighbor) for neighbor in possib]
# pos = {0: (0,0), 1: (1,1), 2: (1,-1), 3: (2,1), 4: (2,-1), 5:(3,0)}
# for e in edges:
#     print(e)
#     Gprim.add_edge(*e)
#     nx.draw_networkx(Gprim)
#     plt.show()
#     Gprim.remove_edge(*e)    