from colorama import Style
import sys
import os
from core import screen, settings, supaparse, encoder, exit_program
import grid

program_data = {
    "ascii": ['MMP""MM""YMM  .M"""bgd        `7MM"""YMM  ',
              'P\'   MM   `7 ,MI    "Y          MM    `7  ',
              '     MM      `MMb.   `7MMpdMAo. MM   d    ',
              '     MM        `YMMNq. MM   `Wb MMmmMM    ',
              '     MM      .     `MM MM    M8 MM   Y  , ',
              '     MM      Mb     dM MM   ,AP MM     ,M ',
              '   .JMML.    P"Ybmmd"  MMbmmd\'.JMMmmmmMMM ',
              '                       MM                 ',
              '                     .JMML.               '],
    "name": "TSpE",
    "author": "MF366",
    "copyright": "Copyright (C) 2024  MF366",
    "description": "Terminal Supaplex Editor"
}


if len(sys.argv) > 1:
    PARSER = settings.SettingsParser(sys.argv[1])
    
else:
    PARSER = settings.SettingsParser(os.path.join(os.path.dirname(__file__), 'core', 'settings.json'))

cur_dir: str = os.getcwd()

# [*] Home screen setup
def change_directory(path: str):
    '''
    TODO
    '''
    
    global cur_dir
    
    if not os.path.exists(path):
        raise FileNotFoundError('the selected path does not exist')
    
    elif path == '..':
        cur_dir = os.path.dirname(cur_dir)
    
    elif path == '~':
        cur_dir = os.path.expanduser('~')
        
    else:
        cur_dir = path
        
    return f"Working Directory is now set to: {cur_dir}\n!/CURRENTRENDERCONTEXTASISNOCHANGE/"

home_cd_args = [screen.Argument('path')]

home_commands = [screen.Command('cd', home_cd_args)]
home_scrn = screen.Context('Home Screen')

SCREEN = screen.Screen(PARSER.colormap, )

