from configparser import ConfigParser, SectionProxy
import pandapower as pp


def load_system(bus_number: int, config_file: str = "config.ini") -> pp.pandapowerNet:
    config = _config_data_load(config_file)
    data_path = config["data_path"]
    base_file = config["base_file"]
    bus_file = config["bus_file"]
    branch_file = config["branch_file"]

    bus_number = str(bus_number)
    base = _base_load(data_path + base_file + bus_number)
    base_mva = float(base["Potência base(kVA)"].replace(",", ".")) / 1e3
    net = pp.create_empty_network(f_hz=60, sn_mva=base_mva)
    net = _bus_load(data_path + bus_file + bus_number, net, base)
    net = _branch_load(data_path + branch_file + bus_number, net)
    return net


def get_parameters_config(config_file: str = "config.ini") -> SectionProxy:
    config = ConfigParser()
    config.read(config_file)
    return config["parameters"]


def _config_data_load(file: str) -> SectionProxy:
    config = ConfigParser()
    config.read(file)
    return config["data"]


def _base_load(path_file: str) -> SectionProxy:
    base = ConfigParser()
    base.read(path_file, encoding="utf8")
    return base["default"]


def _branch_load(path_file: str, net: pp.pandapowerNet) -> pp.pandapowerNet:
    with open(path_file, "r") as file:
        line = file.readline()
        while line:
            line = line.split()
            from_bus = int(line[0])
            to_bus = int(line[1])
            resis = float(line[2].replace(",", "."))
            reat = float(line[3].replace(",", "."))
            line = pp.create_line_from_parameters(
                net=net,
                from_bus=from_bus,
                to_bus=to_bus,
                length_km=1,
                r_ohm_per_km=resis,
                x_ohm_per_km=reat,
                c_nf_per_km=0,
                max_i_ka=1e6,
            )
            pp.create_switch(net, from_bus, line, "l")
            pp.create_switch(net, to_bus, line, "l")
            line = file.readline()
    return net


def _bus_load(
    path_file: str, net: pp.pandapowerNet, base_config: SectionProxy
) -> pp.pandapowerNet:
    tensao_base = base_config["Tensão base(kV)"].replace(",", ".")
    max_vm = base_config["Tensão máxima(pu)"].replace(",", ".")
    min_vm = base_config["Tensão mínima(pu)"].replace(",", ".")
    ref_bus = int(base_config["Barra de referência"])
    with open(path_file, "r") as file:
        line = file.readline()
        while line:
            line = line.split()
            n_bus = int(line[0])
            pKw = float(line[1].replace(",", ".", 1))
            qiKvar = float(line[2].replace(",", ".", 1))
            qcKvar = float(line[3].replace(",", ".", 1))
            pp.create_bus(
                net, tensao_base, index=n_bus, max_vm_pu=max_vm, min_vm_pu=min_vm
            )
            pp.create_load(net, n_bus, pKw / 1e3, (qiKvar - qcKvar) / 1e3)
            if n_bus != ref_bus:
                pp.create_gen(
                    net,
                    n_bus,
                    min_p_mw=-10,
                    max_p_mw=10,
                    min_q_mvar=-5,
                    max_q_mvar=5,
                    in_service=False,
                    min_vm_pu=min_vm,
                    max_vm_pu=max_vm,
                    controllable=True,
                )
            line = file.readline()
    pp.create_ext_grid(net, ref_bus)
    return net
