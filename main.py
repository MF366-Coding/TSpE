from colorama import Style
import simple_webbrowser
import sys
import os
import math
from core import screen, settings, supaparse, encoder, exit_program
import grid

# pylint: disable=W0603
# pylint: disable=W0123

# [i] my plans for the next coding sessions are:
# [*] FINISH THE GODDAMN OUTSIDE FUNCTIONS AND TEST THE DAMN SCREEN!
# TODO


class TagError(Exception): ...
class FileExtensionError(Exception): ...
class SupaplexStructureError(Exception): ...


FIXME = grid.CHANGE_ME_LATER
RENDER_CONTEXT = '!/CURRENTRENDERCONTEXTASISNOCHANGE/'
DEFAULT_PLACEHOLDER = "default.value.placeholder.check.for.existing.value"

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

cur_grid: grid.Grid | None = None

home_scrn = screen.Context('Home Screen', FIXME)
editor_scrn = screen.Context("Level Editor", FIXME)


# [*] Home screen setup
def about_tspe() -> str:
    return f"TSpE - Terminal Supaplex Editor is a backwards-compatible Supaplex level editor made by MF366\n\n{RENDER_CONTEXT}"


def change_directory(path: str) -> str:
    global cur_dir

    if not os.path.exists(path):
        raise FileNotFoundError('the selected path does not exist')

    if path == '..':
        cur_dir = os.path.dirname(cur_dir)

    elif path == '~':
        cur_dir = os.path.expanduser('~')

    else:
        cur_dir = path

    return f"Working Directory is now set to: {cur_dir}\n\n{RENDER_CONTEXT}"


def delete_file_or_folder(path: str) -> str:
    if not PARSER.allow_del:
        raise PermissionError('deleting files/directories from the disk is disabled')

    exists_as_given: bool = os.path.exists(path)
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, path))
    path_to_remove = False

    if exists_as_given:
        path_to_remove: str = path

    elif exists_as_joint_path:
        path_to_remove: str = os.path.join(cur_dir, path)

    else:
        raise FileNotFoundError('the selected path does not exist')

    if os.path.isdir(path_to_remove):
        os.removedirs(path_to_remove)

    else:
        os.remove(path_to_remove)

    return f"'{path_to_remove}' sucessfully removed!\n\n{RENDER_CONTEXT}"


def dump_tspe_settings() -> str:
    PARSER.save_reload()
    return f"Settings loaded!\n\n{RENDER_CONTEXT}"


def echo_like_command(what: str, path: str = None):
    echoed_contents: str = ' '.join(what.split('\n'))

    if not path:
        return f"{echoed_contents}\n\n{RENDER_CONTEXT}"

    exists_as_given: bool = os.path.exists(path)
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, path))
    path_to_write = False

    if exists_as_given:
        path_to_write: str = path

    elif exists_as_joint_path:
        path_to_write = os.path.join(cur_dir, path)

    else:
        raise FileNotFoundError('the selected path does not exist')

    if not os.path.isfile(path_to_write):
        raise BufferError("can't write to an object that isn't a file")

    else:
        with open(path_to_write, 'a', encoding='\n') as f:
            f.write(f'\n{echoed_contents}')

    return f"Appended contents to {path_to_write}\n\n{RENDER_CONTEXT}"


def evaluate_pythonic_expression(expression: str):
    if not PARSER.allow_eval:
        raise PermissionError('evaluating Python expressions is disabled')
    
    evaluated_exp = eval(expression, math.__dict__)
    
    # [*] Result is bool
    if evaluated_exp == 0 or evaluated_exp == 1:
        for char in ('=', '<', '>'):
            if char not in expression:
                continue
            
            final_exp = bool(evaluated_exp)
            break
    
    # [*] Result is a float but is equal an integer
    elif isinstance(evaluated_exp, float):
        if evaluated_exp == int(evaluated_exp):
            final_exp = int(evaluated_exp)
            
    else:
        final_exp = evaluated_exp
        
    return f'Result: {str(final_exp).strip()}\n\n{RENDER_CONTEXT}'


def change_directory_alternative(tagname: str) -> str:
    if tagname in ('..', '*', '~'):
        raise TagError("such tag is not allowed - even if it's on the JSON file, it cannot be accepted by TSpE")
    
    try:
        tagpath: str = PARSER.tags[tagname]
    
    except KeyError:
        tagpath: str = tagname
        
    return change_directory(path=tagpath)


def reload_tspe_settings() -> str:
    PARSER.force_reload()
    return f"Settings have been reloaded!\n\n{RENDER_CONTEXT}"


def new_level_on_editor(path: str, template_name: str = 'BLANK') -> screen.Context:
    global cur_grid
    
    if not path.lower().endswith('.sp') and not PARSER.allow_weird_extensions:
        raise FileExtensionError('weird use of file extension - should be SP (to always ignore this error, change "ignoreWeirdUseOfFileExtensions" in settings to true)')
    
    if template_name not in PARSER.templates:
        level_details: dict[str, list[int]] = supaparse.generate_empty_sp_level()
        
    else:
        template_contents: bytearray = supaparse.get_file_contents_as_bytearray(PARSER.templates[template_name])
        level_details: dict[str, list[int]] = supaparse.interpret_sp_data(template_contents)
    
    cur_grid = grid.Grid(level_details, PARSER.supaplex_element_database, PARSER.element_display_type, PARSER.grid_cell_capacity, 1)
    editor_scrn.update_state(cur_grid.render_grid())
    
    return editor_scrn
    

def open_level_on_editor(path: str) -> screen.Context:
    global cur_grid
    
    if not path.lower().endswith('.sp') and not PARSER.allow_weird_extensions:
        raise FileExtensionError('weird use of file extension - should be SP (to always ignore this error, change "ignoreWeirdUseOfFileExtensions" in settings to true)')

    exists_as_given: bool = os.path.exists(path)
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, path))
    path_to_open = False

    if exists_as_given:
        path_to_open: str = path

    elif exists_as_joint_path:
        path_to_open: str = os.path.join(cur_dir, path)
        
    else:
        raise FileNotFoundError("is the path correct?")
    
    level_details: dict[str, list[int]] = supaparse.interpret_sp_data(supaparse.get_file_contents_as_bytearray(path_to_open))
    
    cur_grid = grid.Grid(level_details, PARSER.supaplex_element_database, PARSER.element_display_type, PARSER.grid_cell_capacity, 1)
    editor_scrn.update_state(cur_grid.render_grid())
    
    return editor_scrn


def open_spfix_documentation() -> str:
    simple_webbrowser.website("https://github.com/MF366-Coding/The-Ultimate-Supaplex-Archive/blob/d04be7b765bb9c50a9eb014527aef688fc483556/Supaplex_Stuff/Documentation/SPFIX63a.pdf")
    return RENDER_CONTEXT



# [*] Editor/Grid Commands
def edit_level_properties(infotrons: int = -1, gravity: bool | int = -1, frozen_zonks: bool | int = -1, level_name: str = "default.name.placeholder.check.for.existing.name") -> str:
    if infotrons > 255:
        raise SupaplexStructureError("max number of needed infotrons mustn't exceed 255")
    
    if infotrons >= 0:
        cur_grid.level['number_of_infotrons_needed'] = infotrons
        
    if gravity >= 0:
        gravity = supaparse.clamp_value(gravity, 0, 8)
        cur_grid.level['initial_gravitation'] = [gravity]
        
    if frozen_zonks >= 0:
        if frozen_zonks > 2:
            frozen_zonks = 0
        
        frozen_zonks = supaparse.clamp_value(frozen_zonks, 1, 2)
        cur_grid.level['initial_freeze_zonks'] = [frozen_zonks]
        
    if level_name != DEFAULT_PLACEHOLDER:
        bytetitle: list[int] = supaparse.string_to_bytetitle(level_name)
        cur_grid.level['level_title'] = bytetitle
        
    return f"Changes applied!\n\n{cur_grid.render_grid()}"


def change_level_borders(new_item: int) -> str:
    border_up: list[int] = cur_grid.get_index_from_selection(x1=0, y1=0, x2=59, y2=0)
    border_down: list[int] = cur_grid.get_index_from_selection(x1=0, y1=23, x2=59, y2=23)
    border_left: list[int] = cur_grid.get_index_from_selection(x1=0, y1=0, x2=0, y2=23)
    border_right: list[int] = cur_grid.get_index_from_selection(x1=59, y1=0, x2=59, y2=23)
    
    for index in border_down + border_left + border_right + border_up:
        cur_grid.change_element_by_index(index, new_item)
    
    return f"Done!\n\n{cur_grid.render_grid()}"


def change_item_in_grid(x: int, y: int, new_item: int) -> str:
    if x > 59:
        raise ValueError('X value cannot be greater than 59')
    
    if y > 23:
        raise ValueError('Y value cannot be greater than 23')
    
    if x < 0:
        raise ValueError('X value cannot be lower than 0')
    
    if y < 0:
        raise ValueError('Y value cannot be lower than 0')
    
    cur_grid.change_element_by_coordinate(x, y, new_item)
    
    return f"Item at ({x}, {y}) changed to {new_item} sucessfully\n\n{cur_grid.render_grid()}"


def change_grid_with_checkers_pattern(x1: int, y1: int, x2: int, y2: int, item_1: int, item_2: int) -> str:
    if x1 > 59 or x2 > 59:
        raise ValueError('X values cannot be greater than 59')
    
    if y1 > 23 or y2 > 23:
        raise ValueError('Y values cannot be greater than 23')
    
    if x1 < 0 or x2 < 0:
        raise ValueError('X values cannot be lower than 0')
    
    if y1 < 0 or y2 < 0:
        raise ValueError('Y values cannot be lower than 0')
    
    selection_table: list[int] = cur_grid.get_index_from_selection(x1, y1, x2, y2)
    
    for num, index in enumerate(selection_table, 0):
        if num == 0 or num % 2 == 0:
            item = item_1
            
        else:
            item = item_2
        
        cur_grid.change_element_by_index(index, item)
        
    return f"Checkers board recreated at ({x1}, {y1}) - ({x2}, {y2}) using elements {item_1} and {item_2}.\n\n{cur_grid.render_grid()}"
    

def fill_square_area(x1: int, y1: int, x2: int, y2: int, item: int) -> str:
    if x1 > 59 or x2 > 59:
        raise ValueError('X values cannot be greater than 59')
    
    if y1 > 23 or y2 > 23:
        raise ValueError('Y values cannot be greater than 23')
    
    if x1 < 0 or x2 < 0:
        raise ValueError('X values cannot be lower than 0')
    
    if y1 < 0 or y2 < 0:
        raise ValueError('Y values cannot be lower than 0')
    
    selection_table: list[int] = cur_grid.get_index_from_selection(x1, y1, x2, y2)
    
    for index in selection_table:        
        cur_grid.change_element_by_index(index, item)
        
    return f"Filled selection ({x1}, {y1}) - ({x2}, {y2}) with element {item} sucessfully.\n\n{cur_grid.render_grid()}"


home_cd_del_args: list[screen.Argument] = [screen.Argument('path')]
home_echo_args: list[screen.Argument, screen.OptionalArgument] = [screen.Argument('what'), screen.OptionalArgument('path', '')]
home_eval_args: list[screen.Argument] = [screen.Argument('expression')]
home_cd_alt_args: list[screen.Argument] = [screen.Argument('tagname')]
home_new_level_args: list[screen.Argument, screen.OptionalArgument] = [screen.Argument('path'), screen.OptionalArgument('template_name', 'BLANK')]

home_commands: list[screen.Command] = [
    screen.Command('about', [], about_tspe),
    screen.Command('cd', home_cd_del_args, change_directory),
    screen.Command('delete', home_cd_del_args, delete_file_or_folder),
    screen.Command('del', home_cd_del_args, delete_file_or_folder), # [i] Forgot to implement aliases - too late now - so this is how I'm gonna do it
    screen.Command('dump', [], dump_tspe_settings),
    screen.Command('echo', home_cd_del_args, echo_like_command),
    screen.Command('evaluate', home_eval_args, evaluate_pythonic_expression),
    screen.Command('eval', home_eval_args, evaluate_pythonic_expression),
    screen.Command('goto', home_cd_alt_args, change_directory_alternative),
    screen.Command('go', home_cd_alt_args, change_directory_alternative),
    screen.Command('load', [], reload_tspe_settings),
    screen.Command('new', home_new_level_args, new_level_on_editor),
    screen.Command('n', home_new_level_args, new_level_on_editor),
    screen.Command('nl', home_new_level_args, new_level_on_editor),
    screen.Command('open', home_cd_del_args, open_level_on_editor),
    screen.Command('o', home_cd_del_args, open_level_on_editor),
    screen.Command('ol', home_cd_del_args, open_level_on_editor),
    screen.Command('spfix', [], open_spfix_documentation)
]

editor_commands = [
    screen.Command("attributes", FIXME, FIXME),
]

home_scrn.add_several_commands(home_commands)

SCREEN = screen.Screen(PARSER.colormap, home_scrn)

