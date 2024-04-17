from core import encoder, screen, supaparse, settings

# [*] Defining constants for easier and faster access
CHANGEMELATER = CHANGE_ME_LATER = 'change.me.please'

HORIZONTAL_SEPARATOR: str = chr(9472)

TOP_LEFT_CORNER: str = chr(9556)
TOP_RIGHT_CORNER: str = chr(9559)

BOTTOM_LEFT_CORNER: str = chr(9562)
BOTTOM_RIGHT_CORNER: str = chr(9565)

VERTICAL_LINE: str = chr(9553)

GRIDLINE, TOPL, TOPR, BOTL, BOTR, HSEP = VERTICAL_LINE, TOP_LEFT_CORNER, TOP_RIGHT_CORNER, BOTTOM_LEFT_CORNER, BOTTOM_RIGHT_CORNER, HORIZONTAL_SEPARATOR


def int_to_hex_string(n: int) -> str:
    return f'{f"{n:02x}".upper()}h'


class Grid:
    def __init__(self, level_data: dict[str, list[int]], level_num: int = 1, part_of_levelset: bool = False) -> None:
        self._LEVEL: dict[str, list[int]] = level_data.copy()
        self._GRID: list[int] = self._LEVEL['level']
        
        if level_num < 10:
            self._level_num: str = f'00{level_num}'
            
        elif 9 < level_num < 99:
            self._level_num: str = f"0{level_num}"
            
        else:
            self._level_num: str = str(level_num)
    
    def convert_display_type(self, element: int, display_type: str) -> str:
        """
        TODO
        """
        
        match display_type:
            case 'hexadecimal' | 'hex':
                return int_to_hex_string(element)
            
            case _:
                return element
        
    def __str__(self) -> str:
        '''
        FIXME
        '''
        
        temp: list[str] = [self.convert_display_type(self._GRID[i], CHANGE_ME_LATER).center(2, ' ') + '|' for i in range(24)]
        aux = temp * 2
        
        for index, elem in enumerate(temp, 0):
            if index == 0 or index % 2 == 0:
                aux[index] = f"║{elem[:-1]}║"
                
            else:
                aux[index] = '║================================================================================================================================================================================================================================================║'
            
        temp: str = '\n'.join(temp)
        
        return f"""

LEVEL {self._level_num}: {supaparse.bytes_to_string(self._LEVEL['level_title'])}
Gravity {'OFF' if not self._LEVEL['initial_gravitation'] else 'ON'} | Frozen Zonks {'ON' if self._LEVEL['initial_freeze_zonks'] == 2 else 'OFF'}
{CHANGEMELATER} / {self._LEVEL['number_of_infotrons_needed'] if self._LEVEL['number_of_infotrons_needed'] != 0 else CHANGEMELATER} Infotrons | {CHANGEMELATER} Electrons
{CHANGEMELATER} special ports ─ ╚ ╝ ╔ ╗ ║
╔================================================================================================================================================================================================================================================╗
{temp}
╚================================================================================================================================================================================================================================================╝


"""
