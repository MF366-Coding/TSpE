from core import supaparse


class CapacityError(Exception): ...
class ElementError(Exception): ...
class ByteError(Exception): ...


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
    def __init__(self, level_data: dict[str, list[int]], element_db: dict[str, list[str, str, None | bool, bool | None, bool | None]], display_type: str | int = 0, cell_capacity: int = 5, level_num: int = 1, width: int = 60, height: int = 24, filepath: str | None = None) -> None:
        """
        __init__ setups the Grid

        Args:
            level_data (dict[str, list[int]]): the actual level contents
            cell_capacity (int, optional): how many characters are allowed per grid cell. Defaults to 5, minimum allowed is 4.
            level_num (int, optional): purely visual, used as an indicator when dealing with levels inside levelsets. Defaults to 1.
            width (int, optional): the level's width. Backwards compatible levels (SP levels) must have 60 as width. Defaults to 60.
            height (int, optional): the level's height. Backwards compatible levels (SP levels) must have 24 as height. Defaults to 24.

        Raises:
            CapacityError: the cell capacity for the grid is lower than 4
        """
        
        self._LEVEL: dict[str, list[int]] = level_data.copy()
        
        self._infotrons: int = self._LEVEL['level'].count(4)
        self._exits: int = self._LEVEL['level'].count(7)
        self._murphies: int = self._LEVEL['level'].count(3)
        
        if cell_capacity < 4:
            raise CapacityError('the cell capacity for the grid must be higher than 4')
        
        number_of_signs: int = cell_capacity * (width + 1) + width
        
        self._DISPLAY_AREA = [0, 59, False]
        
        self._CELL_CAPACITY: int = cell_capacity
        self._GIVEN_PATH = filepath
        
        self.HORIZONTAL_SEPARATOR: str = '=' * number_of_signs
        self.HSEP: str = self.HORIZONTAL_SEPARATOR
        
        self._WIDTH: int = width
        self._HEIGHT: int = height
        
        if level_num < 10:
            self._level_num: str = f'00{level_num}'
            
        elif 9 < level_num < 99:
            self._level_num: str = f"0{level_num}"
            
        else:
            self._level_num: str = str(level_num)
        
        match display_type:
            case 'hex' | 'hexadecimal' | 1:
                self._ELEM_DISPLAY_TYPE = 'hexadecimal'
            
            case 'symbol' | 2:
                self._ELEM_DISPLAY_TYPE = 'symbol'
                
            case _:
                self._ELEM_DISPLAY_TYPE = 'integer'
                
        self._ELEM_DATABASE = element_db
    
    def find_special_port_id(self, hi: int, lo: int) -> int:
        for var_id in range(1, 11):
            var_port = self._LEVEL[f'special_port{var_id}']
            
            if var_port[0] == hi and var_port[1] == lo:
                return var_id
            
        return 0
    
    def get_coord_from_index(self, index: int) -> tuple[int, int]:
        y, x = divmod(index, self._WIDTH)
        return x, y
    
    def get_index_from_coord(self, x: int, y: int) -> int:
        return y * self._WIDTH + x

    def get_index_from_selection(self, x1: int, y1: int, x2: int, y2: int) -> list[int]:
        items: list[int] = []
        
        if x1 > x2:
            raise ValueError('x2 must be lower than x1')
        
        if y1 > y2:
            raise ValueError('y2 must be lower than y1')
        
        column_spacing = x2 - x1 + 1
        line_spacing = y2 - y1 + 1
        
        for i in range(line_spacing):
            if i != 0:
                if items[-1] == self.get_index_from_coord(x2, y2):
                    break
                
            for j in range(column_spacing):
                items.append(self.get_index_from_coord(j + x1, i + y1))
        
        return items
    
    def change_element_by_index(self, index: int, element: int) -> None:
        x, y = self.get_coord_from_index(index)
        
        if element > 255:
            raise ByteError("a byte cannot hold a value greater than 255")
        
        if element in (13, 14, 15, 16) and self._LEVEL['number_of_special_ports'][0] >= 10:
            raise ElementError("reached maximum amount of special ports")
        
        if self._LEVEL['level'][index] in (13, 14, 15, 16):
            hi, lo = supaparse.calculate_special_port_hi_lo(x, y)
            
            aux: dict[str, list[int]] = self._LEVEL.copy()
            
            for key, value in self._LEVEL.items():
                if not key.startswith('special_port'):
                    continue
                
                if value[0] == hi and value[1] == lo:
                    aux[key] = [0] * 6
                    aux['number_of_special_ports'][0] -= 1
                
                self._LEVEL = aux
                    
        elif self._LEVEL['level'][index] == 4:
            self._infotrons -= 1
        
        elif self._LEVEL['level'][index] == 3:
            self._murphies -= 1
            
        elif self._LEVEL['level'][index] == 7:
            self._exits -= 1
            
        if element in (13, 14, 15, 16):
            hi, lo = supaparse.calculate_special_port_hi_lo(x, y)
            
            aux: dict[str, list[int]] = self._LEVEL.copy()
            
            for key, value in self._LEVEL.items():
                if not key.startswith('special_port'):
                    continue
                
                if value == [0] * 6:
                    aux[key] = [hi, lo, 0, 0, 0, 0]
                    aux['number_of_special_ports'][0] += 1
                
                self._LEVEL = aux
                
        elif element == 4:
            self._infotrons += 1
        
        elif element == 3:
            self._murphies += 1
            
        elif element == 7:
            self._exits += 1
            
        self._LEVEL['level'][index] = element
    
    def change_element_by_coordinate(self, x: int, y: int, element: int) -> None:
        matching_index: int = self.get_index_from_coord(x, y)
        
        self.change_element_by_index(matching_index, element)
    
    @property
    def level(self) -> dict[str, list[int]]:
        return self._LEVEL
    
    @property
    def filepath(self) -> str:
        return self._GIVEN_PATH
    
    @property
    def level_number(self) -> str:
        return self._level_num
    
    def calculate_number_of_signs(self, width: int) -> int:
        return self._CELL_CAPACITY * (width + 1) + width
    
    def render_grid(self) -> str:
        if self._DISPLAY_AREA == [0, 59, False]:     
            visual_grid: str = f"{VERTICAL_LINE}{'y/x'.center(self._CELL_CAPACITY)}{VERTICAL_LINE}"
            
            for i in range(self._HEIGHT + 1):
                if i == 0:
                    eggs = ''
                    
                    for j in range(self._WIDTH):
                        eggs += f"{str(j).center(self._CELL_CAPACITY)}{VERTICAL_LINE}"
                    
                    eggs += '\n'
                    visual_grid += f"{eggs}{VERTICAL_LINE}{self.HSEP}{VERTICAL_LINE}\n{VERTICAL_LINE}"
                    continue
                
                visual_grid += f"{str(i - 1).center(self._CELL_CAPACITY)}{VERTICAL_LINE}" 
                    
                for k in range(self._WIDTH):
                    spam: str = self.convert_display_type(element=self._LEVEL['level'][self.get_index_from_coord(k, i - 1)]).center(self._CELL_CAPACITY, ' ')
                    
                    if len(spam) > self._CELL_CAPACITY:
                        raise CapacityError('an element that has a bigger lenght than the capacity was received but is not allowed')
                    
                    visual_grid += f"{spam}{VERTICAL_LINE}"
                    
                visual_grid += f'\n║{self.HSEP}║\n║'
            
            list_grid = visual_grid.split('\n')[0:-2]
            visual_grid = '\n'.join(list_grid)
            
            return f"""
========== DISPLAYING ALL COLUMNS ==========
LEVEL {self._level_num}: {supaparse.bytes_to_string(self._LEVEL['level_title'])}
Gravity {'OFF' if not self._LEVEL['initial_gravitation'][0] else 'ON'} | Frozen Zonks {'ON' if self._LEVEL['initial_freeze_zonks'][0] == 2 else 'OFF'}
{self._infotrons} / {self._LEVEL['number_of_infotrons_needed'][0] if self._LEVEL['number_of_infotrons_needed'][0] != 0 else f'{self._infotrons} (All)'} Infotrons | {self._LEVEL['level'].count(24)} Electrons
{self._LEVEL['number_of_special_ports'][0]} special ports
╔{self.HSEP}╗
{visual_grid}
╚{self.HSEP}╝


"""

        if self._DISPLAY_AREA[2]:
            visual_grid: str = f"{VERTICAL_LINE}{'y/x'.center(self._CELL_CAPACITY)}{VERTICAL_LINE}"
            
            for i in range(self._HEIGHT + 1):
                if i == 0:
                    eggs = ''
                    
                    for j in self._DISPLAY_AREA[:2]:
                        eggs += f"{str(j).center(self._CELL_CAPACITY)}{VERTICAL_LINE}"
                    
                    eggs += '\n'
                    visual_grid += f"{eggs}{VERTICAL_LINE}{'=' * (self._CELL_CAPACITY * 3 + 2)}{VERTICAL_LINE}\n{VERTICAL_LINE}"
                    continue
                
                visual_grid += f"{str(i - 1).center(self._CELL_CAPACITY)}{VERTICAL_LINE}"
                
                for k in self._DISPLAY_AREA[:2]:
                    spam = self.convert_display_type(element=self._LEVEL['level'][self.get_index_from_coord(k, i - 1)]).center(self._CELL_CAPACITY, ' ')
                    
                    if len(spam) > self._CELL_CAPACITY:
                        raise CapacityError('an element that has a bigger lenght than the capacity was received but is not allowed')
                    
                    visual_grid += f"{spam}{VERTICAL_LINE}"
                    
                visual_grid += f'\n║{"=" * (self._CELL_CAPACITY * 3 + 2)}║\n║'
            
            list_grid = visual_grid.split('\n')[0:-2]
            visual_grid = '\n'.join(list_grid)
            
            return f"""
========== DISPLAYING COLUMNS {self._DISPLAY_AREA[0]} AND {self._DISPLAY_AREA[1]} ==========
LEVEL {self._level_num}: {supaparse.bytes_to_string(self._LEVEL['level_title'])}
Gravity {'OFF' if not self._LEVEL['initial_gravitation'][0] else 'ON'} | Frozen Zonks {'ON' if self._LEVEL['initial_freeze_zonks'][0] == 2 else 'OFF'}
{self._infotrons} / {self._LEVEL['number_of_infotrons_needed'][0] if self._LEVEL['number_of_infotrons_needed'][0] != 0 else f'{self._infotrons} (All)'} Infotrons | {self._LEVEL['level'].count(24)} Electrons
{self._LEVEL['number_of_special_ports'][0]} special ports
╔{'=' * (self._CELL_CAPACITY * 3 + 2)}╗
{visual_grid}
╚{'=' * (self._CELL_CAPACITY * 3 + 2)}╝


"""

        visual_grid = f"{VERTICAL_LINE}{'y/x'.center(self._CELL_CAPACITY)}{VERTICAL_LINE}"
        
        __tup = tuple(range(self._DISPLAY_AREA[0], self._DISPLAY_AREA[1] + 1))
        
        for i in range(self._HEIGHT + 1):
            if i == 0:
                eggs = ''
                
                for j in range(self._DISPLAY_AREA[0], self._DISPLAY_AREA[1] + 1):
                    eggs += f"{str(j).center(self._CELL_CAPACITY)}{VERTICAL_LINE}"
                    
                eggs += '\n'
                visual_grid += f"{eggs}{VERTICAL_LINE}{'=' * self.calculate_number_of_signs(len(__tup))}{VERTICAL_LINE}\n{VERTICAL_LINE}"
                continue
            
            visual_grid += f"{str(i - 1).center(self._CELL_CAPACITY)}{VERTICAL_LINE}"
            
            for k in range(self._DISPLAY_AREA[0], self._DISPLAY_AREA[1] + 1):
                spam = self.convert_display_type(self._LEVEL['level'][self.get_index_from_coord(k, i - 1)]).center(self._CELL_CAPACITY, ' ')
                
                if len(spam) > self._CELL_CAPACITY:
                    raise CapacityError('an element that has a bigger lenght than the capacity was received but is not allowed')
                    
                visual_grid += f"{spam}{VERTICAL_LINE}"
                
            visual_grid += f'\n║{"=" * self.calculate_number_of_signs(len(__tup))}║\n║'
            
        list_grid = visual_grid.split('\n')[0:-2]
        visual_grid = '\n'.join(list_grid)
            
        return f"""
========== DISPLAYING COLUMNS {self._DISPLAY_AREA[0]} TO {self._DISPLAY_AREA[1]} ==========
LEVEL {self._level_num}: {supaparse.bytes_to_string(self._LEVEL['level_title'])}
Gravity {'OFF' if not self._LEVEL['initial_gravitation'][0] else 'ON'} | Frozen Zonks {'ON' if self._LEVEL['initial_freeze_zonks'][0] == 2 else 'OFF'}
{self._infotrons} / {self._LEVEL['number_of_infotrons_needed'][0] if self._LEVEL['number_of_infotrons_needed'][0] != 0 else f'{self._infotrons} (All)'} Infotrons | {self._LEVEL['level'].count(24)} Electrons
{self._LEVEL['number_of_special_ports'][0]} special ports
╔{'=' * self.calculate_number_of_signs(len(__tup))}╗
{visual_grid}
╚{'=' * self.calculate_number_of_signs(len(__tup))}╝


"""

    def convert_display_type(self, element: int) -> str:
        match self._ELEM_DISPLAY_TYPE:
            case 'hexadecimal' | 'hex':
                return int_to_hex_string(n=element)
            
            case 'symbol':
                if self._ELEM_DATABASE is None or self._ELEM_DATABASE[str(element)] is None or self._ELEM_DATABASE[str(element)][1] is None:
                    raise ElementError('the element\'s symbol is set to None')
                
                return self._ELEM_DATABASE[str(element)][1]
            
            case _:
                return str(element)
        
    def __str__(self) -> str:
        return self.render_grid()
    
    def __setitem__(self, key: str, value: object) -> None:
        if key == 'colFULL':
            self._DISPLAY_AREA = [0, 59, False] # [<] screw the motherfucking value
        
        elif key == "colLEFT":
            self._DISPLAY_AREA[0] = value
            
        elif key == 'colRIGHT':
            self._DISPLAY_AREA[1] = value
            
        elif key == 'colLOGIC':
            self._DISPLAY_AREA[2] = True if value == '%' else False

        else:
            raise ValueError(f'cannot set {key} - even if it is valid, it cannot be set through __setitem__')
    
    @property
    def murphy_count(self):
        return self._murphies
    
    @property
    def infotron_count(self):
        return self._infotrons
    
    @property
    def exit_count(self):
        return self._exits
