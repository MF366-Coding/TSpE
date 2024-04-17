from core import encoder, screen, supaparse, settings

# [*] Defining constants for easier and faster access
CHANGEMELATER = CHANGE_ME_LATER = 'change.me.please'

HORIZONTAL_SEPARATOR: str = '=' * 359

TOP_LEFT_CORNER: str = chr(9556)
TOP_RIGHT_CORNER: str = chr(9559)

BOTTOM_LEFT_CORNER: str = chr(9562)
BOTTOM_RIGHT_CORNER: str = chr(9565)

VERTICAL_LINE: str = chr(9553)

GRIDLINE, TOPL, TOPR, BOTL, BOTR, HSEP = VERTICAL_LINE, TOP_LEFT_CORNER, TOP_RIGHT_CORNER, BOTTOM_LEFT_CORNER, BOTTOM_RIGHT_CORNER, HORIZONTAL_SEPARATOR


def int_to_hex_string(n: int) -> str:
    return f'{f"{n:02x}".upper()}h'


class Grid:
    def __init__(self, level_data: dict[str, list[int]], level_num: int = 1, part_of_levelset: bool = False, height: int = 24, width: int = 60) -> None:
        self._LEVEL: dict[str, list[int]] = level_data.copy()
        self._GRID: list[int] = self._LEVEL['level']
        
        self._WIDTH = width
        self._HEIGHT = height
        
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
        
        visual_grid: str = VERTICAL_LINE
        
        for i in range(self._HEIGHT):
            for _ in range(self._WIDTH):
                visual_grid += f"{self.convert_display_type(self._GRID[i], CHANGE_ME_LATER).center(5, ' ')}{VERTICAL_LINE}"
                
            visual_grid += f'\n║{HORIZONTAL_SEPARATOR}║\n║'
        
        visual_grid = '\n'.join(visual_grid.split('\n')[0:-2])
        
        return f"""

LEVEL {self._level_num}: {supaparse.bytes_to_string(self._LEVEL['level_title'])}
Gravity {'OFF' if not self._LEVEL['initial_gravitation'] else 'ON'} | Frozen Zonks {'ON' if self._LEVEL['initial_freeze_zonks'] == 2 else 'OFF'}
{CHANGEMELATER} / {self._LEVEL['number_of_infotrons_needed'] if self._LEVEL['number_of_infotrons_needed'] != 0 else CHANGEMELATER} Infotrons | {CHANGEMELATER} Electrons
{CHANGEMELATER} special ports ─ ╚ ╝ ╔ ╗ ║
╔{HORIZONTAL_SEPARATOR}╗
{visual_grid}
╚{HORIZONTAL_SEPARATOR}╝


"""
