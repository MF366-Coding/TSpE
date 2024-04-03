"""
supaparse.py

FIXME

This module allows you to read, interpret and write to SP and DAT files.
"""


def read_sp_file(filename: str) -> bytearray:
    """
    read_sp_file allows for storing the contents of an SP file as a bytearray

    Args:
        filename (str): the path to the file

    Returns:
        bytearray: the contents of the SP file
    """
    
    with open(filename, 'rb') as f:
        data = bytearray(f.read())
    
    return data


def interpret_sp_data(data: bytearray) -> dict[str, bytearray]:
    """
    interpret_sp_data interprets the contents of a SP file

    Args:
        data (bytearray): the contents of the SP file

    Returns:
        dict[str, bytearray]: relation key - value, with strings as keys, bytearrays as values
    """
    
    level: dict[str, bytearray] = {
        'level': data[:1440],
        'unused': data[1440:1444],
        'initial_gravitation': bytearray(data[1444]),
        'space': bytearray(data[1445]),
        'level_title': data[1446:1469],
        'initial_freeze_zonks': bytearray(data[1469]),
        'number_of_infotrons_needed': bytearray(data[1470]),
        'number_of_special_ports': bytearray(data[1471]),
        'special_port1': data[1472:1478],
        'special_port2': data[1478:1484],
        'special_port3': data[1484:1490],
        'special_port4': data[1490:1496],
        'special_port5': data[1496:1502],
        'special_port6': data[1502:1508],
        'special_port7': data[1508:1514],
        'special_port8': data[1514:1520],
        'special_port9': data[1520:1526],
        'special_port10': data[1526:1532]
    }
    
    return level


def format_back_sp_data(level: dict[str, bytearray]) -> bytearray:
    data = bytearray()
    
    for value in level.values():
        data.extend(value)
        
    return data


def write_sp_file(filename: str, level: dict[str, bytearray] | bytearray):
    if isinstance(level, dict):
        level = format_back_sp_data(level)
        
    with open(filename, 'wb') as f:
        f.write(level)


class DATFile:
    """
    DATFile

    Class for working with DAT files (DOS Supaplex Levelsets)
    
    By itself, it can write to any file with any extension but usually levelsets have either one of 2 extensions:
    - DAT
    - Dxy, where x is a number between 0 and 9 and y is between 1 and 9
    """


def read_dat_file(filename: str):
    """
    BUG
    """
    
    with open(filename, 'rb') as f:
        data = bytearray(f.read())

    return data


def interpret_dat_data(data: bytearray) -> list:
    """
    BUG
    """
    
    levels: list[dict[str, bytearray]] = []
    
    for i in range(0, len(data), 1536):
        level_data: bytearray = data[i:i+1536]
        
        level: dict[str, bytearray] = {
            'level': level_data[:1440],
            'unused': level_data[1440:1444],
            'initial_gravitation': bytearray(level_data[1444]),
            'space': bytearray(level_data[1445]),
            'level_title': level_data[1446:1469],
            'initial_freeze_zonks': bytearray(level_data[1469]),
            'number_of_infotrons_needed': bytearray(level_data[1470]),
            'number_of_special_ports': bytearray(level_data[1471]),
            'special_port1': level_data[1472:1478],
            'special_port2': level_data[1478:1484],
            'special_port3': level_data[1484:1490],
            'special_port4': level_data[1490:1496],
            'special_port5': level_data[1496:1502],
            'special_port6': level_data[1502:1508],
            'special_port7': level_data[1508:1514],
            'special_port8': level_data[1514:1520],
            'special_port9': level_data[1520:1526],
            'special_port10': level_data[1526:1532]
        }
        
        levels.append(level)
        
    if len(levels) > 111:
        levels = levels[:111]
        
    elif len(levels) < 111:
        for i in range(0, 111 - len(levels)):
            levels.append({
                'level': bytearray([0] * 1440),
                'unused': bytearray([0] * 4),
                'initial_gravitation': bytearray([0]),
                'space': bytearray([0]),
                'level_title': bytearray([0] * 23),
                'initial_freeze_zonks': bytearray([0]),
                'number_of_infotrons_needed': bytearray([0]),
                'number_of_special_ports': bytearray([0]),
                'special_port1': bytearray([0] * 6),
                'special_port2': bytearray([0] * 6),
                'special_port3': bytearray([0] * 6),
                'special_port4': bytearray([0] * 6),
                'special_port5': bytearray([0] * 6),
                'special_port6': bytearray([0] * 6),
                'special_port7': bytearray([0] * 6),
                'special_port8': bytearray([0] * 6),
                'special_port9': bytearray([0] * 6),
                'special_port10': bytearray([0] * 6)
            })

    return levels


def write_dat_file(filename: str, levels: list[dict[str, bytearray]]):
    """
    BUG
    """
    
    data = bytearray()
    
    for level in levels[:111]:
        for level_data in level.values():
            data.extend(level_data[:1536])
    
    with open(filename, 'wb') as f:
        f.write(data)


def string_to_bytes(string: str) -> list[int]:
    return [ord(i) for i in string]
    

def bytes_to_string(bytes_iterable) -> str:
    return "".join([chr(i) for i in bytes_iterable])
    
    
def string_to_bytetitle(title: str, **options) -> list[int]:
    fillchar = options.get("fillchar", "-")

    title = title.upper().strip()
    
    if len(title) > 23:
        raise ValueError("title too long (max 23 characters)")
        
    title = title.center(23, fillchar)
    
    if title[-1] != fillchar and title[0] == fillchar:
        title = title[0:22] + fillchar
    
    return string_to_bytes(title)


def calculate_special_port_pos(hi: int, lo: int) -> tuple[int, int]:
    offset: float = (256 * hi + lo) / 2
    
    y = int(offset / 60)
    x = int(offset - 60 * y)
    
    return x, y


def calculate_special_port_hi_lo(x: int, y: int) -> tuple[int, int]:
    value = ((y * 60) + x) * 2
    
    hi = int(value / 256)
    lo = int(value % 256)
    
    return hi, lo
