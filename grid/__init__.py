from core import encoder, screen, supaparse, settings

class Grid:
    def __init__(self, level_data: dict[str, list[int]], level_num: int = 1, part_of_dat: bool = False) -> None:
        self._LEVEL = level_data.copy()
        self._GRID = self._LEVEL['level']
        
        if level_num < 10:
            self._level_num: str = f'00{level_num}'
            
        elif 9 < level_num < 99:
            self._level_num: str = f"0{level_num}"
            
        else:
            self._level_num: str = str(level_num)
        
    def __str__(self) -> str:
        return f"""
    Level {self._level_num}: {self._LEVEL['level_title']}
    {'Gravity' if self._LEVEL['initial_gravitation']}
    """
        