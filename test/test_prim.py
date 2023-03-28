import sys
sys.path.append('.')
from OSDEE import OSDEE
import unittest

class TestPrimMethods(unittest.TestCase):
    def test_prim(self):
        for i in (14, 33, 84, 136, 415):
            sys = OSDEE(i)
            mst = sys.prim.mst()
            OSDEE.set_net_from_graph(sys.net, mst)
            sys.run_power_flow(sys.net)