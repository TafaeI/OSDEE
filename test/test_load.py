import sys

sys.path.append('.')
from OSDEE.__src__ import load


def show():
    net = load._load_system(14)


if __name__ == '__main__':
    show()