from OSDEE import OSDEE
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("system", type=int)
    args = parser.parse_args()
    sys = OSDEE(args.system)
    graph = sys.prim.mst(sys.prim._base_graph)
    net = sys.set_net_from_graph(sys.net, graph)
    sys._save_result_in_path(
        "./resultados/prim/" + str(args.system), net, sys.get_network_id(net)
    )
