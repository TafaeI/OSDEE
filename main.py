from OSDEE import OSDEE
import argparse

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('system', type=int)
    args = parser.parse_args()
    sys = OSDEE(args.system)