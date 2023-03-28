from configparser import ConfigParser, SectionProxy
import pandapower as pp


def _load_system(bus_number: int,
                 config_file: str = 'config.ini') -> pp.pandapowerNet:
    config = _config_load(config_file)
    bus_number = str(bus_number)
    base = _base_load(config['data_path'] + config['base_file'] + bus_number)
    net = pp.create_empty_network(
        f_hz=60,
        sn_mva=float(base['Potência base(kVA)'].replace(',', '.')) * 1e3)
    net = _bus_load(config['data_path'] + config['bus_file'] + bus_number, net,
                    base)
    net = _branch_load(
        config['data_path'] + config['branch_file'] + bus_number, net)
    return net


def _config_load(file: str) -> SectionProxy:
    config = ConfigParser()
    config.read(file)
    return config['default']


def _base_load(path_file: str) -> SectionProxy:
    base = ConfigParser()
    base.read(path_file, encoding='utf8')
    return base['default']


def _branch_load(path_file: str, net: pp.pandapowerNet) -> pp.pandapowerNet:
    with open(path_file, 'r') as file:
        line = file.readline()
        while line:
            line = line.split()
            from_bus = int(line[0])
            to_bus = int(line[1])
            resis = float(line[2].replace(',', '.'))
            reat = float(line[3].replace(',', '.'))
            pp.create_line_from_parameters(net=net, from_bus=from_bus, to_bus=to_bus, length_km=1,
                                           r_ohm_per_km=resis, x_ohm_per_km=reat, c_nf_per_km=0, max_i_ka=1e6)
            line = file.readline()
    return net


def _bus_load(path_file: str, net: pp.pandapowerNet,
              base_config: SectionProxy) -> pp.pandapowerNet:
    tensao_base = base_config['Tensão base(kV)'].replace(',', '.')
    max_vm = base_config['Tensão máxima(pu)'].replace(',', '.')
    min_vm = base_config['Tensão mínima(pu)'].replace(',', '.')
    with open(path_file, 'r') as file:
        line = file.readline()
        while line:
            line = line.split()
            n_bus = int(line[0])
            pKw = float(line[1].replace(',', '.', 1))
            qiKvar = float(line[2].replace(',', '.', 1))
            qcKvar = float(line[3].replace(',', '.', 1))
            pp.create_bus(net,
                          tensao_base,
                          index=n_bus,
                          max_vm_pu=max_vm,
                          min_vm_pu=min_vm)
            pp.create_load(net, n_bus, pKw / 1e3, (qiKvar - qcKvar) / 1e3)
            line = file.readline()
        return net
