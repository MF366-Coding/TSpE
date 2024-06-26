import json
from colorama import Fore, Back, Style


COLORMAP_CONVERSION_TABLE = [
    Style.RESET_ALL,
    Style.BRIGHT,
    Style.DIM,
    Style.NORMAL,
    Fore.RESET,
    Fore.BLUE,
    Fore.CYAN,
    Fore.YELLOW,
    Fore.RED,
    Fore.GREEN,
    Fore.MAGENTA,
    Fore.WHITE,
    Fore.BLACK,
    Back.RESET,
    Back.BLUE,
    Back.CYAN,
    Back.YELLOW,
    Back.RED,
    Back.GREEN,
    Back.MAGENTA,
    Back.WHITE,
    Back.BLACK,
    Fore.LIGHTBLUE_EX,
    Fore.LIGHTCYAN_EX,
    Fore.LIGHTYELLOW_EX,
    Fore.LIGHTRED_EX,
    Fore.LIGHTGREEN_EX,
    Fore.LIGHTMAGENTA_EX,
    Fore.LIGHTWHITE_EX,
    Fore.LIGHTBLACK_EX,
    Back.LIGHTBLUE_EX,
    Back.LIGHTCYAN_EX,
    Back.LIGHTYELLOW_EX,
    Back.LIGHTRED_EX,
    Back.LIGHTGREEN_EX,
    Back.LIGHTMAGENTA_EX,
    Back.LIGHTWHITE_EX,
    Back.LIGHTBLACK_EX
]


class SettingsParser:
    def __init__(self, path: str) -> None:
        self._path = path
        self._settings: dict[str, dict[str, str] | bool] | None = None
        self._get_settings()

    def _get_settings(self) -> None:
        with open(self._path, 'r', encoding='utf-8') as f:
            self._settings = json.load(f)

    def save_settings(self) -> None:
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(self._settings, f, indent=4)

    def save_reload(self) -> None:
        self.save_settings()
        self._get_settings()

    def force_reload(self, path: str | None = None) -> None:
        self._path: str = path if path is not None else self._path
        self._get_settings()

    @property
    def settings(self) -> dict[str, dict[str, str] | bool | int | str]:
        return self._settings

    @property
    def colormap(self) -> dict[str | int]:
        return {k: COLORMAP_CONVERSION_TABLE[v] for k, v in self._settings['colormap'].items()}
    
    @property
    def templates(self) -> dict[str, str]:
        return self._settings['templates']

    @property
    def testers(self) -> dict[str, str]:
        return self._settings['testProviders']
    
    @property
    def supaplex_element_database(self) -> dict[str, list[str, str, bool | None, bool, bool]]:
        return self._settings['spElems']

    @property
    def tags(self) -> dict[str, str]:
        return self._settings['tags']

    @property
    def element_display_type(self) -> str:
        return self._settings['elemDisplayType']

    @property
    def allow_eval(self) -> bool:
        return self._settings['allowEvaluate']

    @property
    def allow_del(self) -> bool:
        return self._settings['allowDelete']

    @property
    def online_help(self) -> bool:
        return self._settings['useOnlineHelp']

    @property
    def logging(self) -> bool:
        return self._settings['logging']
    
    @property
    def allow_weird_extensions(self) -> bool:
        return self._settings["ignoreWeirdUseOfFileExtensions"]
    
    @property
    def grid_cell_capacity(self) -> int:
        return self._settings['cellCapacity']

    test_providers: property = testers
