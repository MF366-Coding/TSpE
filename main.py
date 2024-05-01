from colorama import Style
import sys
import os
from core import screen, settings, supaparse, encoder, exit_program
import grid

# pylint: disable=W0603

# [i] my plans for the next coding sessions are:
# [*] FINISH THE GODDAMN OUTSIDE FUNCTIONS AND TEST THE DAMN SCREEN!
# TODO

FIXME = grid.CHANGE_ME_LATER

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

home_scrn = screen.Context('Home Screen', FIXME)


# [*] Home screen setup
def change_directory(path: str):
    global cur_dir
    
    if not os.path.exists(path):
        raise FileNotFoundError('the selected path does not exist')
    
    if path == '..':
        cur_dir = os.path.dirname(cur_dir)
    
    elif path == '~':
        cur_dir = os.path.expanduser('~')
        
    else:
        cur_dir = path
        
    return f"Working Directory is now set to: {cur_dir}\n\n!/CURRENTRENDERCONTEXTASISNOCHANGE/"


def delete_file_or_folder(path: str):
    if not PARSER.allow_del:
        raise PermissionError('deleting files/directories from the disk is disabled')
    
    exists_as_given: bool = os.path.exists(path)
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, path))
    path_to_remove = False
    
    if exists_as_given:
        path_to_remove = path
        
        if os.path.isdir(path_to_remove):
            os.removedirs(path_to_remove)
        
        else:
            os.remove(path_to_remove)
            
    elif exists_as_joint_path:
        path_to_remove = os.path.join(cur_dir, path)
        
        if os.path.isdir(path_to_remove):
            os.removedirs(path_to_remove)
        
        else:
            os.remove(path_to_remove)
    
    else:
        raise FileNotFoundError('the selected path does not exist')
    
    return f"'{path_to_remove}' sucessfully removed!\n\n!/CURRENTRENDERCONTEXTASISNOCHANGE/"


home_cd_del_args = [screen.Argument('path')]
home_commands = [screen.Command('cd', home_cd_del_args, change_directory), screen.Command('delete', home_cd_del_args, delete_file_or_folder), screen.Command('del', home_cd_del_args, delete_file_or_folder)]

home_scrn.add_several_commands(home_commands)

SCREEN = screen.Screen(PARSER.colormap, home_scrn)

