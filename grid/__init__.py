from core import encoder, screen, supaparse, settings


class CapacityError(Exception): ...
class ElementError(Exception): ...


# [*] Defining constants for easier and faster access
CHANGEMELATER = CHANGE_ME_LATER = 'FIXME'

TOP_LEFT_CORNER: str = chr(9556)
TOP_RIGHT_CORNER: str = chr(9559)

BOTTOM_LEFT_CORNER: str = chr(9562)
BOTTOM_RIGHT_CORNER: str = chr(9565)

VERTICAL_LINE: str = chr(9553)

GRIDLINE, TOPL, TOPR, BOTL, BOTR = VERTICAL_LINE, TOP_LEFT_CORNER, TOP_RIGHT_CORNER, BOTTOM_LEFT_CORNER, BOTTOM_RIGHT_CORNER


def int_to_hex_string(n: int) -> str:
    return f'{f"{n:02x}".upper()}h'


class Grid:
    def __init__(self, level_data: dict[str, list[int]], level_num: int = 1, cell_capacity: int = 5, part_of_levelset: bool = False, width: int = 60, height: int = 24) -> None:
        self._LEVEL: dict[str, list[int]] = level_data.copy()
        self._GRID: list[int] = self._LEVEL['level']
        
        if cell_capacity < 3:
            raise CapacityError('the cell capacity for the grid must be higher than 3')
        
        number_of_signs: int = cell_capacity * width + width - 1
        
        self._CELL_CAPACITY = cell_capacity
        
        self.HORIZONTAL_SEPARATOR: str = '=' * number_of_signs
        self.HSEP = self.HORIZONTAL_SEPARATOR
        
        self._WIDTH = width
        self._HEIGHT = height
        
        if level_num < 10:
            self._level_num: str = f'00{level_num}'
            
        elif 9 < level_num < 99:
            self._level_num: str = f"0{level_num}"
            
        else:
            self._level_num: str = str(level_num)
            
    def get_index_from_coord(self, x: int, y: int) -> int:
        return x * self._WIDTH + y

    def get_index_from_selection(self, x1: int, x2: int, y1: int, y2: int) -> list[int]:
        items: list[int] = [self.get_index_from_coord(x1, y1)]
        
        for _ in range(self._WIDTH // (x2 - x1)):
            if items[-1] >= self.get_index_from_coord(x2, y2):
                break
        
            for _ in range(y2 - y1):
                items.append(items[-1] + 1)
                
            items.append(items[-(y2 - y1) - 1] + self._WIDTH)
        
        items.pop(-1)
        
        return items
    
    def change_index(self, x: int, y: int, element: int):
        '''
        TODO
        '''
        
        if element > 255:
            return
    
    def render_grid(self) -> str:
        visual_grid: str = VERTICAL_LINE
        
        for i in range(self._HEIGHT):
            for _ in range(self._WIDTH):
                spam: str = self.convert_display_type(self._GRID[i], CHANGE_ME_LATER).center(self._CELL_CAPACITY, ' ')
                
                if len(spam) > self._CELL_CAPACITY:
                    raise CapacityError('an element that has a bigger lenght than the capacity was received but is not allowed')
                
                visual_grid += f"{spam}{VERTICAL_LINE}"
                
            visual_grid += f'\n║{self.HSEP}║\n║'
        
        visual_grid = '\n'.join(visual_grid.split('\n')[0:-2])
        
        return f"""

LEVEL {self._level_num}: {supaparse.bytes_to_string(self._LEVEL['level_title'])}
Gravity {'OFF' if not self._LEVEL['initial_gravitation'] else 'ON'} | Frozen Zonks {'ON' if self._LEVEL['initial_freeze_zonks'] == 2 else 'OFF'}
{CHANGEMELATER} / {self._LEVEL['number_of_infotrons_needed'] if self._LEVEL['number_of_infotrons_needed'] != 0 else CHANGEMELATER} Infotrons | {CHANGEMELATER} Electrons
{CHANGEMELATER} special ports
╔{self.HSEP}╗
{visual_grid}
╚{self.HSEP}╝


"""

    def convert_display_type(self, element: int, display_type: str, element_config: list[str, str, None | bool, bool | None, bool | None] = None) -> str:
        match display_type:
            case 'hexadecimal' | 'hex':
                return int_to_hex_string(element)
            
            case 'symbol':
                if element_config is None or element_config[1] is None:
                    raise ElementError('the element\'s symbol is set to None')
                
                return element_config[1]
            
            case _:
                return str(element)
        
    def __str__(self) -> str:
        return self.render_grid()
        
