"""
supaparse.py

This module allows you to read, interpret and write to SP and DAT files.
"""

BYTES_PER_SP_FILE = 1536
BYTES_PER_DAT_FILE = 1536 * 111


def get_file_contents_as_bytearray(filename: str) -> bytearray:
    """
    get_file_contents_as_bytearray allows for storing the contents of a file as a bytearray

    Args:
        filename (str): the path to the file

    Returns:
        bytearray: the first 1536 bytes of the file
    """
    
    with open(filename, 'rb') as f:
        data = bytearray(f.read())[:BYTES_PER_SP_FILE]
    
    return data


def interpret_sp_data(data: bytearray) -> dict[str, list[int]]:
    """
    interpret_sp_data interprets the contents of a SP file

    Args:
        data (bytearray): the contents of the SP file

    Returns:
        dict[str, list[int]]: relation key - value, with strings as keys, lists with integers as values
    """
    
    level: dict[str, list[int]] = {
        'level': list(data[:1440]),
        'unused': list(data[1440:1444]),
        'initial_gravitation': [data[1444]],
        'space': [data[1445]],
        'level_title': list(data[1446:1469]),
        'initial_freeze_zonks': [data[1469]],
        'number_of_infotrons_needed': [data[1470]],
        'number_of_special_ports': [data[1471]],
        'special_port1': list(data[1472:1478]),
        'special_port2': list(data[1478:1484]),
        'special_port3': list(data[1484:1490]),
        'special_port4': list(data[1490:1496]),
        'special_port5': list(data[1496:1502]),
        'special_port6': list(data[1502:1508]),
        'special_port7': list(data[1508:1514]),
        'special_port8': list(data[1514:1520]),
        'special_port9': list(data[1520:1526]),
        'special_port10': list(data[1526:1532]),
        'demo': list(data[1532:1536])
    }
    
    return level


def format_back_sp_data(level: dict[str, list[int]]) -> bytearray:
    """
    format_back_sp_data formats a dict back to the bytearray

    Args:
        level (dict[str, list[int]]): the level as a dict

    Returns:
        bytearray: the level as a bytearray
    """
    
    data = bytearray()
    
    for value in level.values():
        data.extend(value)
        
    return data


def write_sp_file(filename: str, level: dict[str, list[int]] | bytearray):
    """
    write_sp_file writes the level as a bytearray to the file at path filename

    If level is already a bytearray, it skips to saving.
    
    If the level is still of type dict, it first converts it to bytearray.

    Args:
        filename (str): savepath
        level (dict[str, list[int]] | bytearray): level to save
    """
    
    if isinstance(level, dict):
        level = format_back_sp_data(level)
        
    with open(filename, 'wb') as f:
        f.write(level)


class SupaplexLevelsetFile:
    """
    SupaplexLevelsetFile

    Class for working with DAT files (DOS Supaplex Levelsets)
    
    By itself, it can write to any file with any extension but usually levelsets have either one of 2 extensions:
    - DAT
    - Dxy, where x is a number between 0 and 9 and y is between 1 and 9
    """
    
    def __init__(self, filename: str):
        """
        __init__ gathers the levelset details from file at path filename

        Args:
            filename (str): levelset path
        """
        
        self._FILENAME: str = filename
        self._levelset: list[dict[str, list[int]]] = None
        self.reload_levelset()
    
    def reload_levelset(self):
        """
        reload_levelset loads and interprets the levelset
        """
        
        self._interpret_levelset(self._read_file(self._FILENAME))
    
    def _read_file(self, filename: str) -> bytearray:
        """
        _read_file gathers the levelset details as one huge bytearray

        Args:
            filename (str): levelset path

        Returns:
            bytearray: levelset data
        """
        
        with open(filename, 'rb') as f:
            data = bytearray(f.read())[:170496]

        return data

    def _interpret_levelset(self, contents: bytearray):
        """
        _interpret_levelset converts the contents of a levelset (bytearray) into a list with multiple dicts

        This actually uses a loop and `interpret_sp_data` under the hood
        
        Args:
            contents (bytearray): the levelset data as a list of dictionaries
        """
        
        self._levelset = []
        
        for level_num in range(111):
            cur_iter = level_num * BYTES_PER_SP_FILE
            self._levelset.append(interpret_sp_data(contents[cur_iter:cur_iter + BYTES_PER_SP_FILE]))
            
    def save_to_file(self, filepath: str):
        """
        save_to_file save the levelset the filepath

        Args:
            filepath (str)
        """
        
        with open(filepath, 'wb') as f:
            for level in self._levelset:
                f.write(format_back_sp_data(level))
    
    @property
    def levelset(self) -> list[dict[str, list[int]]]:
        """
        levelset lets you access and mutate _levelset list

        NOTE: Using __getitem__ is a much better solution (a.k.a. by doing [x])

        Returns:
            list[dict[str, list[int]]]: levelset list, where each level is a dictionary
        """
        
        return self._levelset
    
    def __getitem__(self, level_num: int) -> dict[str, list[int]]:
        return self._levelset[level_num]
    
    def __str__(self) -> str:
        return str(self._levelset)
                
    write_file = save_to_file


def generate_empty_sp_level() -> dict[str, list[int]]:
    return interpret_sp_data(bytearray([0] * BYTES_PER_SP_FILE))


def generate_empty_dat_as_dict() -> dict[str, list[int]]:
    return interpret_sp_data(bytearray([0] * BYTES_PER_DAT_FILE))


def string_to_bytes(string: str) -> list[int]:
    """
    string_to_bytes converts a string to bytes using `ord`

    Args:
        string (str): string to convert

    Returns:
        list[int]: list of bytes (I prefer lists over bytearrays)
    """
    
    return [ord(i) for i in string]
    

def bytes_to_string(bytes_iterable: list[int] | bytearray) -> str:
    """
    bytes_to_string converts an iterable of bytes to a string using `chr`

    Args:
        bytes_iterable (list[int] or bytearray; in theory, any iterable that contains integers): iterable of bytes

    Returns:
        str: string as readable ASCII
    """
    
    return "".join([chr(i) for i in bytes_iterable])

    
def string_to_bytetitle(title: str) -> list[int]:
    """
    string_to_bytetitle applies the logic of `string_to_bytes` (even using it!) but applies rules

    Level title rules (according to SPFIX docs):
    
        1. The string must have 23 characters or less.
        2. A dash (-) is used as fill character.
        3. The string is converted as ASCII uppercase.
        4. The string has no more than 1 trailing whitespace in each side.

    Args:
        title (str): the string to convert to bytes - the title of the level

    Raises:
        ValueError: the first rule is disrespected

    Returns:
        list[int]: a list with bytes that represent the characters 
    """
    
    FILLCHAR = '-'

    title = title.upper()
    
    if len(title) > 23:
        raise ValueError("title too long (max 23 characters)")
        
    title = title.center(23, FILLCHAR)
    
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
