import sys
sys.path.append('.')
from OSDEE import OSDEE
import unittest


class TestVNSMethods(unittest.TestCase):
    @staticmethod
    def _vns_in_system(bus_number: int) -> tuple[float, float]:
        sys = OSDEE(bus_number)
        net = sys.net
        graph = sys.prim.mst(sys.prim._base_graph)
        first_losses = sys.losses(sys.set_net_from_graph(net, graph))
        sys.vns.run(net, graph)
        return first_losses, sys.losses(sys.net)

    def test_vns_14(self):
        self.assertGreaterEqual(*self._vns_in_system(14))

    def test_vns_33(self):
        self.assertGreaterEqual(*self._vns_in_system(33))

    def test_vns_84(self):
        self.assertGreaterEqual(*self._vns_in_system(84))

    def test_vns_136(self):
        self.assertGreaterEqual(*self._vns_in_system(136))

    def test_vns_415(self):
        self.assertGreaterEqual(*self._vns_in_system(415))

if __name__=='__main__':
    sys = OSDEE(415)
    net = sys.net
    graph = sys.prim.mst(sys.prim._base_graph)
    sys.vns.run(net, graph)
    print(sys.losses(sys.net))