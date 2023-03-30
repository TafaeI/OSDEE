from OSDEE import OSDEE
import unittest
from networkx.utils import graphs_equal


class TestGetGraphMethods(unittest.TestCase):
    def _get_graph(self, bus_number):
        sys = OSDEE(bus_number)
        graph = sys.prim.mst(sys.prim._base_graph)
        net = OSDEE.set_net_from_graph(net, graph)
        new_graph = OSDEE.get_graph_from_net(net)
        self.assertTrue(graphs_equal(graph, new_graph))

    def test_get_graph_14(self):
        self._get_graph(14)

    def test_get_graph_33(self):
        self._get_graph(33)

    def test_get_graph_84(self):
        self._get_graph(84)

    def test_get_graph_136(self):
        self._get_graph(136)

    def test_get_graph_415(self):
        self._get_graph(415)
