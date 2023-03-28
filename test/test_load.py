import sys
sys.path.append('.')
from OSDEE.__src__ import load
import pandapower as pp
import unittest

class TestLoadMethods(unittest.TestCase):
    def test_load(self):
        for sys in (14, 33, 84, 136, 415):
            net = load._load_system(sys)
            pp.runpp(net)
