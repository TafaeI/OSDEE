import sys
sys.path.append('.')
from OSDEE import OSDEE
import unittest
import pandapower as pp
import inspect

inspect.stack()[0].function
class TestPrimMethods(unittest.TestCase):
    def test_prim(self):
        pf = lambda x: pp.runpp(x, algorithm='bfsw')
        for i in (14, 33, 84, 136, 415):
            sys = OSDEE(i)
            mst = sys.prim.mst()
            net = OSDEE.set_net_from_graph(sys.net, mst)
            sys.losses(net)

if __name__=='__main__':
    TestPrimMethods().test_prim()