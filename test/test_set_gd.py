from OSDEE import OSDEE
import unittest


class TestSetGdMethods(unittest.TestCase):
    @staticmethod
    def _set_gd(bus_number: int):
        sys = OSDEE(bus_number)
        sys.set_net_from_graph(sys.net, sys.prim.mst(sys.prim._base_graph))
        sys.set_gd_in_buses(sys.net)

    def test_set_gd_14(self):
        self._set_gd(14)

    def test_set_gd_33(self):
        self._set_gd(33)

    def test_set_gd_84(self):
        self._set_gd(84)

    def test_set_gd_136(self):
        self._set_gd(136)

    def test_set_gd_415(self):
        self._set_gd(415)
