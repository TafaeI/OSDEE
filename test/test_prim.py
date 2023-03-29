import sys
sys.path.append('.')
from OSDEE import OSDEE
import unittest
import pandapower as pp
import inspect

inspect.stack()[0].function
class TestPrimMethods(unittest.TestCase):
    @staticmethod
    def _prim(bus_number):
        sys = OSDEE(bus_number)
        mst = sys.prim.mst(sys.prim._base_graph)
        net = OSDEE.set_net_from_graph(sys.net, mst)
        sys.losses(net)

    def test_prim_14(self):
        self._prim(14)
    def test_prim_33(self):
        self._prim(33)
    def test_prim_84(self):
        self._prim(84)
    def test_prim_136(self):
        self._prim(136)
    def test_prim_415(self):
        self._prim(415)
