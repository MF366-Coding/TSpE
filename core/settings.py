import json
from colorama import Fore, Back

def parse_colormap_minimal():
    '''
    XXX
    '''
    
    return {
        "TITLE": Fore.RESET,
        "DESCRIPTION": Fore.RESET,
        "RESET": Fore.RESET,
        "AUTHOR": Fore.RESET,
        "ASCII_PRIMARY": Fore.RESET,
        "ASCII_SECONDARY": Fore.RESET
    }

def parse_colormap():
    """
    TODO
    """
    
    return {
        "TITLE": Fore.YELLOW,
        "DESCRIPTION": Fore.RED,
        "RESET": Fore.RESET,
        "AUTHOR": Fore.BLUE,
        "ASCII_PRIMARY": Fore.BLUE,
        "ASCII_SECONDARY": Fore.GREEN
    }
