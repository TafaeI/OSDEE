import sys
sys.path.append('.')
from OSDEE.__src__ import load
from OSDEE import OSDEE
import pandapower as pp
import unittest
import inspect

class TestLoadMethods(unittest.TestCase):
    @staticmethod
    def _load(bus_number):
        net = load.load_system(bus_number)
        pp.runpp(net)
    def test_load_14(self):
        self._load(14)
    def test_load_33(self):
        self._load(33)
    def test_load_84(self):
        self._load(84)
    def test_load_136(self):
        self._load(136)
    def test_load_415(self):
        self._load(415)

