import sys
sys.path.append('.')
from OSDEE import OSDEE
import unittest


class TestSetNetMethods(unittest.TestCase):
    def _set_net(self, bus_number: int):
        sys = OSDEE(bus_number)
        to_compare = sys.ms.run(10)
        for id in to_compare:
            new_id = sys.get_network_id(sys._set_net_from_id(sys.net, id))
            self.assertEqual(id, new_id)

    def test_set_net_14(self):
        self._set_net(14)

    def test_set_net_33(self):
        self._set_net(33)

    def test_set_net_84(self):
        self._set_net(84)

    def test_set_net_136(self):
        self._set_net(136)

    def test_set_net_415(self):
        self._set_net(415)

if __name__=='__main__':
    sys = OSDEE(14)
    print(sys.net.gen)