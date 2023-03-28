import pandapower as pp
import pandas as pd
import networkx as nx

def get_gen_buses(net: pp.pandapowerNet) -> tuple[int]:
    gen_buses = [g[1].bus for g in net['gen'].iterrows()]
    gen_buses.sort()
    length = len(gen_buses)
    ret = (length,) + tuple(gen_buses)
    return ret

def get_lines_disconnected(net: pp.pandapowerNet) -> tuple[int]:
    switch = net['switch']
    open_switch = switch[switch['closed']==False]
    lines = set(open_switch['element'].values)
    return tuple(sorted(lines))

def _get_line_power_flow(grid: pp.pandapowerNet) -> pd.DataFrame:
    pp.runpp(grid)
    power_flow: pd.Series = grid.get('res_line')['p_from_mw']
    return power_flow

def _get_line_resistence(grid: pp.pandapowerNet) -> pd.DataFrame:
    lines = grid.get('line')
    resistence = lines['length_km']*lines['r_ohm_per_km']
    return resistence

def get_lines_att(grid: pp.pandapowerNet, att: str) -> pd.DataFrame:
    func = _implemented_get_lines_att.get(att)
    if func == None:
        raise Exception(f'Get {att} from grid was not implemented yet')
    ret = func(grid)
    lines = grid.get('line')[['from_bus', 'to_bus']]
    ret = pd.concat([lines,ret], axis=1)
    return ret

_implemented_get_lines_att = {
    'p_from_mw': _get_line_power_flow,
    'resistance': _get_line_resistence
}