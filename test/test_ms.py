import sys
sys.path.append('.')
from OSDEE import OSDEE
import unittest

class TestMSMethods(unittest.TestCase):
    @staticmethod
    def _ms_in_system(bus_num: int):
        sys = OSDEE(bus_num)
        sys.ms.run(100)
    def test_ms_14(self):
        self._ms_in_system(14)
    def test_ms_33(self):
        self._ms_in_system(33)
    def test_ms_84(self):
        self._ms_in_system(84)
    def test_ms_136(self):
        self._ms_in_system(136)
    def test_ms_415(self):
        self._ms_in_system(415)
