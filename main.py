from OSDEE import OSDEE
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('system', type=int)
    args = parser.parse_args()
    sys = OSDEE(args.system)
    ms_group = sys.ms.run(1000)
    after_vns = sys.run_vns_in_ms_systems(sys.net, ms_group)
    sys.save_results(sys.net, after_vns)
