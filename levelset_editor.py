from core import supaparse


class LevelsetEditor:
    def __init__(self, levelset_data: supaparse.SupaplexLevelsetFile, filepath: str | None = None):
        self._LEVELSET: supaparse.SupaplexLevelsetFile = levelset_data
        self._GIVEN_PATH: str | None = filepath
        
    def normalize_levelset(self):
        if len(self._LEVELSET.levelset) > 111:
            self._LEVELSET.levelset = self._LEVELSET.levelset[:111]
            
        elif len(self._LEVELSET.levelset) < 111:
            for _ in range(111 - len(self._LEVELSET.levelset)):
                self._LEVELSET.levelset.append(supaparse.generate_empty_sp_level_as_dict())
        
    def prioritize_edited_levels(self):
        indexes_to_pop: list[int] = []
        
        for index, level in enumerate(self._LEVELSET.levelset, 0):
            if level == supaparse.generate_empty_sp_level_as_dict():
                indexes_to_pop.append(index)

        indexes_to_pop.sort(reverse=True)
        
        for index in indexes_to_pop:
            self._LEVELSET.levelset.pop(index)
        
    def render_list(self):
        levelset_list = "=== TSpE - Levelset Editor ===\n"
        
        for level_num, level in enumerate(self._LEVELSET.levelset, 1):
            levelset_list += f"{str(level_num).center(3)}|| {supaparse.bytes_to_string(level['level_title'])}\n"
            
        levelset_list += "\nWARNING: In case there are less or more than 111 levels, please reload the Levelset Editor."
        
        return levelset_list
        
    @property
    def levelset(self) -> supaparse.SupaplexLevelsetFile:
        return self._LEVELSET
        
    @property
    def filepath(self) -> str | None:
        return self._GIVEN_PATH
    
    def __str__(self):
        return self.render_list()
    