# main.py

import requests
import simple_webbrowser
import sys
import os
import math
import random
import json
from core import screen, settings, supaparse, exit_program, encoder
import levelset_editor
import grid

# pylint: disable=W0603
# pylint: disable=W0123


class TagError(Exception): ...
class FileExtensionError(Exception): ...
class SupaplexStructureError(Exception): ...
class LevelLimitReached(Exception): ...
class LevelNotFoundError(Exception): ...

VERSION = "v0.0.1"
LATEST = None

RENDER_CONTEXT = '!/CURRENTRENDERCONTEXTASISNOCHANGE/' # [!] deprecated, due to buggy behavior
# [!?] technically speaking, the render context special string is still implemented so it can still be used but it's buggy af
DEFAULT_PLACEHOLDER = "default_value_placeholder_check_for_existing_value"
SUPAPLEX_ONLINE_TEST_BASE_URL = 'https://www.supaplex.online/test/#gz,' # [i] thanks Greg :)
TSPE_DIRECTORY = os.path.dirname(__file__)

# TODO
# [!!] i need to test the app gawdamn it!


if len(sys.argv) > 1:
    PARSER = settings.SettingsParser(sys.argv[1])

else:
    PARSER = settings.SettingsParser(os.path.join(os.path.dirname(__file__), 'core', 'settings.json'))

TITLE = f'''

{PARSER.colormap['ASCII_TITLE']}MMP""MM""YMM  .M"""bgd        `7MM"""YMM
P'   MM   `7 ,MI    "Y          MM    `7
     MM      `MMb.   `7MMpdMAo. MM   d
     MM        `YMMNq. MM   `Wb MMmmMM
     MM      .     `MM MM    M8 MM   Y  ,
     MM      Mb     dM MM   ,AP MM     ,M
   .JMML.    P"Ybmmd"  MMbmmd'.JMMmmmmMMM
                       MM
                     .JMML.
{PARSER.colormap['RESET']}
{PARSER.colormap['TITLE_BACKGROUND']}{PARSER.colormap['TITLE_FOREGROUND']}TSpE
{PARSER.colormap['AUTHOR_BACKGROUND']}{PARSER.colormap['AUTHOR_FOREGROUND']}MF366
{PARSER.colormap['RESET_ALL']}Copyright (C) 2024  MF366
{PARSER.colormap['ASCII_TITLE']}Terminal Supaplex Editor'''

cur_dir: str = os.getcwd()

cur_grid: grid.Grid | None = None
cur_levelset_editor: levelset_editor.LevelsetEditor | None = None

home_scrn = screen.Context('Home Screen', TITLE)
editor_scrn = screen.Context("Level Editor", DEFAULT_PLACEHOLDER)
levelset_scrn = screen.Context("Levelset Editor", DEFAULT_PLACEHOLDER)


# [*] Home screen setup
def about_tspe() -> str:
    return f"{PARSER.colormap['INFO_BACKGROUND']}{PARSER.colormap['INFO_FOREGROUND']}TSpE - Terminal Supaplex Editor is a backwards-compatible Supaplex level editor made by MF366{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"


def change_directory(path: str) -> str:
    global cur_dir

    if path == '..':
        cur_dir = os.path.dirname(cur_dir)
        return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Working Directory is now set to: {cur_dir}{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"

    if path == '~':
        cur_dir = os.path.expanduser('~')
        return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Working Directory is now set to: {cur_dir}{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"

    if path == '.':
        # [i] do nothing as a dot means the current directory
        return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Working Directory is now set to: {cur_dir}{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"

    exists_as_given: bool = os.path.exists(path)
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, path))
    path_to_change_to = False

    if exists_as_given:
        path_to_change_to: str = path

    elif exists_as_joint_path:
        path_to_change_to: str = os.path.join(cur_dir, path)

    else:
        raise FileNotFoundError('the selected path does not exist')

    cur_dir = path_to_change_to

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Working Directory is now set to: {cur_dir}{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"


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

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}'{path_to_remove}' sucessfully removed!{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"


def dump_tspe_settings() -> str:
    PARSER.save_reload()
    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Settings loaded!{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"


def echo_like_command(what: str, path: str = None):
    echoed_contents: str = ' '.join(what.split('\n'))

    if not path:
        return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}{echoed_contents}{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"

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
        with open(path_to_write, 'a', encoding='utf-8') as f:
            f.write(f'\n{echoed_contents}')

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Appended contents to {path_to_write}{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"


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

    return f"{PARSER.colormap['INFO_BACKGROUND']}{PARSER.colormap['INFO_FOREGROUND']}Result: {str(final_exp).strip()}{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"


def change_directory_alternative(tagname: str) -> str:
    if tagname in ('..', '*', '~'):
        raise TagError("such tag is not allowed - even if it's in the JSON file, it cannot be accepted by TSpE")

    try:
        tagpath: str = PARSER.tags[tagname]

    except KeyError:
        tagpath: str = tagname

    return change_directory(path=tagpath)


def reload_tspe_settings() -> str:
    PARSER.force_reload()
    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Settings have been reloaded!{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"


def new_level_on_editor(path: str, template_name: str = 'BLANK') -> screen.Context:
    global cur_grid

    if not path.lower().endswith('.sp') and not PARSER.allow_weird_extensions:
        raise FileExtensionError('weird use of file extension - should be SP (to always ignore this error, change "ignoreWeirdUseOfFileExtensions" in settings to true)')

    exists_as_given: bool = os.path.exists(os.path.dirname(path))
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, os.path.dirname(path)))
    path_to_create = False

    if exists_as_given:
        path_to_create: str = path

    elif exists_as_joint_path:
        path_to_create: str = os.path.join(cur_dir, path)

    else:
        raise FileNotFoundError('the selected path does not exist')

    if template_name not in PARSER.templates:
        level_details: dict[str, list[int]] = supaparse.generate_empty_sp_level_as_dict()

    else:
        template_contents: bytearray = supaparse.get_file_contents_as_bytearray(PARSER.templates[template_name])
        level_details: dict[str, list[int]] = supaparse.interpret_sp_data(template_contents)

    supaparse.write_sp_file(path_to_create, level_details)

    cur_grid = grid.Grid(level_details, PARSER.supaplex_element_database, PARSER.element_display_type, PARSER.grid_cell_capacity, 1, filepath=path_to_create)
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

    cur_grid = grid.Grid(level_details, PARSER.supaplex_element_database, PARSER.element_display_type, PARSER.grid_cell_capacity, 1, filepath=path_to_open)
    editor_scrn.update_state(cur_grid.render_grid())

    return editor_scrn


def open_spfix_documentation() -> screen.Context:
    simple_webbrowser.website("https://github.com/MF366-Coding/The-Ultimate-Supaplex-Archive/blob/d04be7b765bb9c50a9eb014527aef688fc483556/Supaplex_Stuff/Documentation/SPFIX63a.pdf")
    return home_scrn


# [*] Editor/Grid Commands
def edit_level_properties(infotrons: int = -1, gravity: bool | int = -1, frozen_zonks: bool | int = -1, level_name: str = "default.name.placeholder.check.for.existing.name") -> str:
    if infotrons > 255:
        raise SupaplexStructureError("max number of needed infotrons mustn't exceed 255")

    if infotrons > 0:
        cur_grid.level['number_of_infotrons_needed'][0] = infotrons

    if gravity >= 0:
        gravity = supaparse.clamp_value(gravity, 0, 1)
        cur_grid.level['initial_gravitation'][0] = gravity

    if frozen_zonks > 0:
        frozen_zonks = supaparse.clamp_value(frozen_zonks, 0, 255) + 1
        cur_grid.level['initial_freeze_zonks'][0] = frozen_zonks

    if level_name != DEFAULT_PLACEHOLDER:
        bytetitle: list[int] = supaparse.string_to_bytetitle(level_name)
        cur_grid.level['level_title'] = bytetitle

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Changes applied!{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def change_level_borders(new_item: int) -> str:
    border_up: list[int] = cur_grid.get_index_from_selection(x1=0, y1=0, x2=59, y2=0)
    border_down: list[int] = cur_grid.get_index_from_selection(x1=0, y1=23, x2=59, y2=23)
    border_left: list[int] = cur_grid.get_index_from_selection(x1=0, y1=0, x2=0, y2=23)
    border_right: list[int] = cur_grid.get_index_from_selection(x1=59, y1=0, x2=59, y2=23)

    for index in border_down + border_left + border_right + border_up:
        cur_grid.change_element_by_index(index, new_item)

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Done!{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


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

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Item at ({x}, {y}) changed to {new_item} sucessfully{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


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

    for index in selection_table:
        x, y = cur_grid.get_coord_from_index(index)
        
        if (x + y) % 2 == 0:
            cur_grid.change_element_by_index(index, item_1)
            
        else:
            cur_grid.change_element_by_index(index, item_2)

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Checker board recreated at ({x1}, {y1}) - ({x2}, {y2}) using elements {item_1} and {item_2}.{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


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

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Filled selection ({x1}, {y1}) - ({x2}, {y2}) with element {item} sucessfully.{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def erase_grid_entry(x: int, y: int) -> str:
    cur_grid.change_element_by_coordinate(x, y, 0)
    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Erased ({x}, {y}) sucessfully{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def fill_grid_with_elem(element: int):
    return fill_square_area(1, 1, 58, 22, element)


def fill_grid_with_elem_alt(element: int):
    return fill_square_area(0, 0, 59, 23, element)


def look_for_element_occurence(element: int, skip_counter: int = 0):
    item_coords: tuple[int, int] | None = None

    for index in range(supaparse.BYTES_PER_SP_LEVEL_DATA):
        if skip_counter < 0:
            break

        if cur_grid.level['level'][index] != element:
            continue

        if cur_grid.level['level'][index] == element:
            if skip_counter >= 0:
                skip_counter -= 1
                item_coords = cur_grid.get_coord_from_index(index)
                continue

    if item_coords is None:
        return f"{PARSER.colormap['WARNING_BACKGROUND']}{PARSER.colormap['WARNING_FOREGROUND']}Element #{element} not found{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"

    return f"{PARSER.colormap['INFO_BACKGROUND']}{PARSER.colormap['INFO_FOREGROUND']}Element #{element} found at ({item_coords[0]}, {item_coords[1]}){PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def edit_special_port_properties(x: int, y: int, gravity: int = -1, frozen_zonks: int = -1, frozen_enemies: int = -1, unused_byte: int = -1):
    if x > 59:
        raise ValueError('X value cannot be greater than 59')

    if y > 23:
        raise ValueError('Y value cannot be greater than 23')

    if x < 0:
        raise ValueError('X value cannot be lower than 0')

    if y < 0:
        raise ValueError('Y value cannot be lower than 0')

    matching_index: int = cur_grid.get_index_from_coord(x, y)

    if cur_grid.level['level'][matching_index] not in (13, 14, 15, 16):
        raise grid.ElementError('selected item is not a special port')

    hi, lo = supaparse.calculate_special_port_hi_lo(x, y)

    special_port_id: int = cur_grid.find_special_port_id(hi, lo)

    if not special_port_id:
        raise grid.ElementError(f"couldn't find a special port with hi {hi} and lo {lo}")

    if gravity >= 0:
        gravity = supaparse.clamp_value(gravity, 0, 8)
        cur_grid.level[f'special_port{special_port_id}'][2] = [gravity]

    if frozen_zonks >= 0:
        if frozen_zonks > 2:
            frozen_zonks = 0

        frozen_zonks = supaparse.clamp_value(frozen_zonks, 1, 2)
        cur_grid.level[f'special_port{special_port_id}'][3] = [frozen_zonks]

    if frozen_enemies >= 0:
        frozen_enemies = supaparse.clamp_value(frozen_enemies, 0, 1)
        cur_grid.level[f'special_port{special_port_id}'][4] = [frozen_enemies]

    if unused_byte >= 0:
        unused_byte = supaparse.clamp_value(unused_byte, 0, 255)
        cur_grid.level[f'special_port{special_port_id}'][5] = [unused_byte]

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Changes applied to port at ({x}, {y})!{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def view_special_port_properties(x: int, y: int):
    if x > 59:
        raise ValueError('X value cannot be greater than 59')

    if y > 23:
        raise ValueError('Y value cannot be greater than 23')

    if x < 0:
        raise ValueError('X value cannot be lower than 0')

    if y < 0:
        raise ValueError('Y value cannot be lower than 0')

    matching_index: int = cur_grid.get_index_from_coord(x, y)

    if cur_grid.level['level'][matching_index] not in (13, 14, 15, 16):
        raise grid.ElementError('selected item is not a special port')

    hi, lo = supaparse.calculate_special_port_hi_lo(x, y)

    special_port_id: int = cur_grid.find_special_port_id(hi, lo)

    if not special_port_id:
        raise grid.ElementError(f"couldn't find a special port with hi {hi} and lo {lo}")

    if cur_grid.level[f'special_port{special_port_id}'][2] > 0:
        gravity_status = 'Gravity ON'

    else:
        gravity_status = 'Gravity OFF'

    if cur_grid.level[f'special_port{special_port_id}'][3] == 2:
        fzonks_status = 'Freeze Zonks'

    else:
        fzonks_status = 'Unfreeze Zonks'

    if cur_grid.level[f'special_port{special_port_id}'][4] == 1:
        fenemies_status = 'Freeze Enemies'

    else:
        fenemies_status = 'Unfreeze Enemies'

    return f"{PARSER.colormap['INFO_BACKGROUND']}{PARSER.colormap['INFO_FOREGROUND']}Port #{special_port_id} at ({x}, {y}): {gravity_status} | {fzonks_status} | {fenemies_status}{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def fill_area_randomly(x1: int, y1: int, x2: int, y2: int, item: int, num: int, keep_intact: int | bool = False):
    if x1 > 59 or x2 > 59:
        raise ValueError('X values cannot be greater than 59')

    if y1 > 23 or y2 > 23:
        raise ValueError('Y values cannot be greater than 23')

    if x1 < 0 or x2 < 0:
        raise ValueError('X values cannot be lower than 0')

    if y1 < 0 or y2 < 0:
        raise ValueError('Y values cannot be lower than 0')

    selection_table: list[int] = cur_grid.get_index_from_selection(x1, y1, x2, y2)

    if num < 1:
        num = len(selection_table)

    for index, match in enumerate(selection_table.copy(), 0):
        if num == 0:
            break

        if random.choice((True, False, False)):
            if keep_intact and cur_grid.level['level'][match] != 0:
                continue

            num -= 1
            selection_table.pop(index)
            continue

    for index in selection_table:
        cur_grid.change_element_by_index(index=index, element=item)

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Randomized item {item} sucessfully.{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def replace_item_for_new_in_area(x1: int, y1: int, x2: int, y2: int, old_item: int, new_item: int) -> str:
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
        if cur_grid.level['level'][index] == old_item:
            cur_grid.change_element_by_index(index, new_item)

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Operation completed with no errors.{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def save_level_sp_format(path: str = '') -> str:
    if not path.split():
        if not cur_grid.filepath:
            cur_levelset_editor.levelset[int(cur_grid.level_number) - 1] = cur_grid.level
            levelset_scrn.update_state(cur_levelset_editor.render_list())
            return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Level version updated! After you're done, quit and save the whole levelset to apply changes.{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"

        supaparse.write_sp_file(cur_grid.filepath, cur_grid.level)
        return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Saved at {cur_grid.filepath}.{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"

    exists_as_given: bool = os.path.exists(os.path.dirname(path))
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, os.path.dirname(path)))
    path_to_create = False

    if exists_as_given:
        path_to_create: str = path

    elif exists_as_joint_path:
        path_to_create: str = os.path.join(cur_dir, path)

    else:
        raise FileNotFoundError('the selected path does not exist')

    supaparse.write_sp_file(path_to_create, cur_grid.level)
    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Saved at {path_to_create}.{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def save_level_sp_format_quit(path: str = '') -> screen.Context:
    save_level_sp_format(path)

    if not cur_grid.filepath:
        return levelset_scrn

    return quit_to_home_scrn()


def test_level_supaplex_online() -> str:
    level_as_bytes: bytearray = supaparse.format_back_sp_data(cur_grid.level)
    compressed_level = encoder.compress_bytes(level_as_bytes)
    encoded_level: bytes = encoder.encode_bytes(compressed_level)

    testing_url = f"{SUPAPLEX_ONLINE_TEST_BASE_URL}{str(encoded_level, encoding='utf-8')}"

    simple_webbrowser.website(testing_url)

    return f"{PARSER.colormap['INFO_BACKGROUND']}{PARSER.colormap['INFO_FOREGROUND']}Testing level...{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def verify_exit_murphy() -> str:
    if cur_grid.murphy_count > 0 and cur_grid.exit_count > 0:
        return f"{PARSER.colormap['INFO_BACKGROUND']}{PARSER.colormap['INFO_FOREGROUND']}The level has Murphies and Exits! Good job :){PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"

    return f"{PARSER.colormap['WARNING_BACKGROUND']}{PARSER.colormap['WARNING_FOREGROUND']}Hmmm... The levels is lacking either Murphies or Exits :({PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def set_selection_outline(x1: int, y1: int, x2: int, y2: int, item: int) -> str:
    if x1 > 59 or x2 > 59:
        raise ValueError('X values cannot be greater than 59')

    if y1 > 23 or y2 > 23:
        raise ValueError('Y values cannot be greater than 23')

    if x1 < 0 or x2 < 0:
        raise ValueError('X values cannot be lower than 0')

    if y1 < 0 or y2 < 0:
        raise ValueError('Y values cannot be lower than 0')

    border_up: list[int] = cur_grid.get_index_from_selection(x1=x1, y1=y1, x2=x2, y2=y1)
    border_down: list[int] = cur_grid.get_index_from_selection(x1=x1, y1=y2, x2=x2, y2=y2)
    border_left: list[int] = cur_grid.get_index_from_selection(x1=x1, y1=y1, x2=x1, y2=y2)
    border_right: list[int] = cur_grid.get_index_from_selection(x1=x2, y1=y1, x2=x2, y2=y2)

    for index in border_down + border_left + border_right + border_up:
        cur_grid.change_element_by_index(index, item)

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Done!{PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def display_element_information(item: int) -> str: # [i] 'wtf' command
    details: list[str, str, bool | None, bool, bool] = PARSER.supaplex_element_database[str(item)]

    name, symbol_code = details[0], details[1]

    if details[2] is True:
        sprite_type = "'Fancy' Sprite"

    elif details[2] is False:
        sprite_type = "'Dull' Sprite"

    else:
        sprite_type = "Regular Sprite"

    destructible: str = 'Destructible' if details[3] is True else "Indestructible"

    explosive: str = 'Explosive' if details[4] is True else 'Not Explosive'

    return f"{PARSER.colormap['INFO_BACKGROUND']}{PARSER.colormap['INFO_FOREGROUND']}Element #{item}: {name} (Symbol {symbol_code}; {sprite_type}; {destructible}; {explosive}){PARSER.colormap['RESET_ALL']}\n\n{cur_grid.render_grid()}"


def quit_to_home_scrn() -> screen.Context:
    home_scrn.update_state(TITLE)
    return home_scrn


def quit_app():
    exit_program.leave_program(PARSER)


def reload_current_screen() -> screen.Context:
    return SCREEN.context


def open_repository_on_browser() -> str:
    simple_webbrowser.website('https://github.com/MF366-Coding/TSpE')
    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}:){PARSER.colormap['RESET_ALL']}\n\n{TITLE}"


def check_for_updates():
    global LATEST

    # [i] If there isn't a cached version...
    if LATEST is None:
        try:
            response = requests.get('https://api.github.com/repos/MF366-Coding/TSpE/releases/latest', timeout=1)
            data = json.loads(response.text)
            LATEST = data['tag_name']

        except requests.RequestException:
            return f"{PARSER.colormap['WARNING_BACKGROUND']}{PARSER.colormap['WARNING_FOREGROUND']}Could not get the latest release :({PARSER.colormap['RESET_ALL']}\n\n{TITLE}"

    return f"{PARSER.colormap['INFO_BACKGROUND']}{PARSER.colormap['INFO_FOREGROUND']}Latest Stable: {LATEST} || Current Version: {VERSION}{PARSER.colormap['RESET_ALL']}\n\n{TITLE}"


def create_new_levelset(path: str):
    global cur_levelset_editor

    exists_as_given: bool = os.path.exists(os.path.dirname(path))
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, os.path.dirname(path)))
    path_to_create = False

    if exists_as_given:
        path_to_create: str = path

    elif exists_as_joint_path:
        path_to_create: str = os.path.join(cur_dir, path)

    else:
        raise FileNotFoundError('the selected path does not exist')

    supaparse.write_sp_file(path_to_create, supaparse.generate_empty_dat_as_bytearray())

    levelset = supaparse.SupaplexLevelsetFile(path_to_create)

    cur_levelset_editor = levelset_editor.LevelsetEditor(levelset, path_to_create)
    levelset_scrn.update_state(cur_levelset_editor.render_list())

    return levelset_scrn


def open_existing_levelset(path: str):
    global cur_levelset_editor

    exists_as_given: bool = os.path.exists(path)
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, path))
    path_to_open = False

    if exists_as_given:
        path_to_open: str = path

    elif exists_as_joint_path:
        path_to_open: str = os.path.join(cur_dir, path)

    else:
        raise FileNotFoundError("is the path correct?")

    levelset = supaparse.SupaplexLevelsetFile(path_to_open)

    cur_levelset_editor = levelset_editor.LevelsetEditor(levelset, path_to_open)
    levelset_scrn.update_state(cur_levelset_editor.render_list())

    return levelset_scrn


def add_level_to_levelset(path: str):
    cur_levelset_editor.normalize_levelset()
    cur_levelset_editor.prioritize_edited_levels()

    if len(cur_levelset_editor.levelset) == 111:
        raise LevelLimitReached('the limit of 111 edited levels in a levelset has been reached and no more can be added')

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
    cur_levelset_editor.levelset.levelset.append(level_details)

    cur_levelset_editor.normalize_levelset()

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Level {path_to_open} has been added to the levelset.{PARSER.colormap['RESET_ALL']}\n\n{cur_levelset_editor.render_list()}"


def create_new_level_inside_levelset():
    cur_levelset_editor.normalize_levelset()
    cur_levelset_editor.prioritize_edited_levels()

    if len(cur_levelset_editor.levelset) == 111:
        raise LevelLimitReached('the limit of 111 edited levels in a levelset has been reached and no more can be added')

    cur_levelset_editor.levelset.levelset.append(supaparse.generate_empty_sp_level_as_dict())
    cur_levelset_editor.normalize_levelset()

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}A new empty level has been added to the levelset.{PARSER.colormap['RESET_ALL']}\n\n{cur_levelset_editor.render_list()}"


def duplicate_level_in_levelset(level_num: int):
    cur_levelset_editor.normalize_levelset()
    cur_levelset_editor.prioritize_edited_levels()

    if len(cur_levelset_editor.levelset) == 111:
        raise LevelLimitReached('the limit of 111 edited levels in a levelset has been reached and no more can be added')

    if level_num > len(cur_levelset_editor.levelset):
        raise LevelNotFoundError(f'level {level_num} does NOT exist')

    level_data = cur_levelset_editor.levelset[level_num - 1]
    cur_levelset_editor.levelset.levelset.append(level_data)
    cur_levelset_editor.normalize_levelset()

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Level {level_num} has been duplicated.{PARSER.colormap['RESET_ALL']}\n\n{cur_levelset_editor.render_list()}"


def edit_level_from_levelset(level_num: int) -> screen.Context:
    global cur_grid

    cur_levelset_editor.normalize_levelset()

    if level_num > len(cur_levelset_editor.levelset):
        raise LevelNotFoundError(f'level {level_num} does NOT exist')

    level_details: dict[str, list[int]] = cur_levelset_editor.levelset[level_num - 1]

    cur_grid = grid.Grid(level_details, PARSER.supaplex_element_database, PARSER.element_display_type, PARSER.grid_cell_capacity, level_num)
    editor_scrn.update_state(cur_grid.render_grid())

    levelset_scrn.update_state(cur_levelset_editor.render_list())

    return editor_scrn


def remove_level_from_levelset(level_num: int):
    cur_levelset_editor.normalize_levelset()

    if level_num > len(cur_levelset_editor.levelset):
        raise LevelNotFoundError(f'level {level_num} does NOT exist')

    cur_levelset_editor.levelset.levelset.pop(level_num - 1)
    cur_levelset_editor.prioritize_edited_levels()
    cur_levelset_editor.normalize_levelset()

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Done.{PARSER.colormap['RESET_ALL']}\n\n{cur_levelset_editor.render_list()}"


def save_levelset(path: str = '') -> str:
    cur_levelset_editor.normalize_levelset()

    if not path:
        cur_levelset_editor.levelset.write_file(cur_levelset_editor.filepath)
        return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Saved at: {cur_levelset_editor.filepath}{PARSER.colormap['RESET_ALL']}\n\n{cur_levelset_editor.render_list()}"

    exists_as_given: bool = os.path.exists(os.path.dirname(path))
    exists_as_joint_path: bool = os.path.exists(os.path.join(cur_dir, os.path.dirname(path)))
    path_to_create = False

    if exists_as_given:
        path_to_create: str = path

    elif exists_as_joint_path:
        path_to_create: str = os.path.join(cur_dir, path)

    else:
        raise FileNotFoundError('the selected path does not exist')

    cur_levelset_editor.levelset.write_file(path_to_create)
    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Saved at: {path_to_create}{PARSER.colormap['RESET_ALL']}\n\n{cur_levelset_editor.render_list()}"


def save_levelset_quit(path: str = '') -> screen.Context:
    save_levelset(path)
    return home_scrn


def swap_levels_in_levelset(level_a: int, level_b: int):
    cur_levelset_editor.normalize_levelset()

    if level_a > len(cur_levelset_editor.levelset) or level_b > len(cur_levelset_editor.levelset):
        raise LevelNotFoundError("at least one of the levels doesn't exist does NOT exist")

    level_b_data: dict[str, list[int]] = cur_levelset_editor.levelset[level_b - 1]
    level_a_data: dict[str, list[int]] = cur_levelset_editor.levelset[level_a - 1]

    cur_levelset_editor.levelset.levelset[level_a - 1] = level_b_data
    cur_levelset_editor.levelset.levelset[level_b - 1] = level_a_data

    cur_levelset_editor.prioritize_edited_levels()
    cur_levelset_editor.normalize_levelset()

    return f"{PARSER.colormap['SUCESSFUL_BACKGROUND']}{PARSER.colormap['SUCESSFUL_FOREGROUND']}Swapped levels {level_a} and {level_b}.{PARSER.colormap['RESET_ALL']}\n\n{cur_levelset_editor.render_list()}"


def quit_level_editor() -> screen.Context:
    if not cur_grid.filepath:
        return levelset_scrn

    return quit_to_home_scrn()


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
    screen.Command('echo', home_echo_args, echo_like_command),
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
    screen.Command('spfix', [], open_spfix_documentation),
    screen.Command('nls', [screen.Argument('path', 'str')], create_new_levelset),
    screen.Command('ols', [screen.Argument('path', 'str')], open_existing_levelset),
    screen.Command('update', [], check_for_updates),
    screen.Command('quit', [], quit_app),
    screen.Command('q', [], quit_app),
    screen.Command('exit', [], quit_app),
    screen.Command('leave', [], quit_app),
    screen.Command('logout', [], quit_app),
    screen.Command('reload', [], reload_current_screen),
    screen.Command('rl', [], reload_current_screen),
    screen.Command('web', [], open_repository_on_browser),
    screen.Command('repo', [], open_repository_on_browser)
]

level_attributes_args: list[screen.OptionalArgument] = [screen.OptionalArgument('infotrons', -1, 'int'), screen.OptionalArgument('gravity', -1, 'int'),
                                                        screen.OptionalArgument('frozen_zonks', -1, 'int'), screen.OptionalArgument(name='level_name', default_value=DEFAULT_PLACEHOLDER)]
editor_change_args: list[screen.Argument] = [screen.Argument('x', 'int'), screen.Argument('y', 'int'), screen.Argument('new_item', 'int')]
editor_checkers_args = [screen.Argument('x1', 'int'), screen.Argument('y1', 'int'), screen.Argument('x2', 'int'), screen.Argument('y2', 'int'), screen.Argument('item_1', 'int'), screen.Argument('item_2', 'int')]
editor_selection_args = [screen.Argument('x1', 'int'), screen.Argument('y1', 'int'), screen.Argument('x2', 'int'), screen.Argument('y2', 'int'), screen.Argument('item', 'int')]
editor_coord_args = [screen.Argument('x', 'int'), screen.Argument('y', 'int')]

editor_commands: list[screen.Command] = [
    screen.Command("attributes", level_attributes_args, edit_level_properties),
    screen.Command("attrs", level_attributes_args, edit_level_properties),
    screen.Command("at", level_attributes_args, edit_level_properties),
    screen.Command("@", level_attributes_args, edit_level_properties),
    screen.Command('borders', [screen.Argument('new_item', 'int')], change_level_borders),
    screen.Command('outline', [screen.Argument('new_item', 'int')], change_level_borders),
    screen.Command('change', editor_change_args, change_item_in_grid),
    screen.Command('ch', editor_change_args, change_item_in_grid),
    screen.Command('checkers', editor_checkers_args, change_grid_with_checkers_pattern),
    screen.Command('chess', editor_checkers_args, change_grid_with_checkers_pattern),
    screen.Command('board', editor_checkers_args, change_grid_with_checkers_pattern),
    screen.Command('container', editor_selection_args, fill_square_area),
    screen.Command('square', editor_selection_args, fill_square_area),
    screen.Command('erase', editor_coord_args, erase_grid_entry),
    screen.Command('er', editor_coord_args, erase_grid_entry),
    screen.Command('fill', [screen.Argument('item', 'int')], fill_grid_with_elem),
    screen.Command('fillall', [screen.Argument('item', 'int')], fill_grid_with_elem_alt),
    screen.Command('match', [screen.Argument('element', 'int'), screen.OptionalArgument('skip_counter', 0, 'int')], look_for_element_occurence),
    screen.Command('portedit', editor_coord_args + [screen.OptionalArgument('gravity', -1, 'int'), screen.OptionalArgument('frozen_zonks', -1, 'int'), screen.OptionalArgument('frozen_enemies', -1, 'int'), screen.OptionalArgument('unused_byte', -1, 'int')], edit_special_port_properties),
    screen.Command('ported', editor_coord_args + [screen.OptionalArgument('gravity', -1, 'int'), screen.OptionalArgument('frozen_zonks', -1, 'int'), screen.OptionalArgument('frozen_enemies', -1, 'int'), screen.OptionalArgument('unused_byte', -1, 'int')], edit_special_port_properties),
    screen.Command('pe', editor_coord_args + [screen.OptionalArgument('gravity', -1, 'int'), screen.OptionalArgument('frozen_zonks', -1, 'int'), screen.OptionalArgument('frozen_enemies', -1, 'int'), screen.OptionalArgument('unused_byte', -1, 'int')], edit_special_port_properties),
    screen.Command('portinfo', editor_coord_args, view_special_port_properties),
    screen.Command('pinfo', editor_coord_args, view_special_port_properties),
    screen.Command('pinf', editor_coord_args, view_special_port_properties),
    screen.Command('random', editor_selection_args + [screen.Argument('num', 'int'), screen.OptionalArgument('keep_intact', False, 'bool')], fill_area_randomly),
    screen.Command('rand', editor_selection_args + [screen.Argument('num', 'int'), screen.OptionalArgument('keep_intact', False, 'bool')], fill_area_randomly),
    screen.Command('replace', [screen.Argument('x1', 'int'), screen.Argument('y1', 'int'), screen.Argument('x2', 'int'), screen.Argument('y2', 'int'), screen.Argument('old_item', 'int'), screen.Argument('new_item', 'int')], replace_item_for_new_in_area),
    screen.Command('rep', [screen.Argument('x1', 'int'), screen.Argument('y1', 'int'), screen.Argument('x2', 'int'), screen.Argument('y2', 'int'), screen.Argument('old_item', 'int'), screen.Argument('new_item', 'int')], replace_item_for_new_in_area),
    screen.Command('save', [screen.OptionalArgument('path', '', 'str')], save_level_sp_format),
    screen.Command('s', [screen.OptionalArgument('path', '', 'str')], save_level_sp_format),
    screen.Command('savequit', [screen.OptionalArgument('path', '', 'str')], save_level_sp_format_quit),
    screen.Command('sq', [screen.OptionalArgument('path', '', 'str')], save_level_sp_format_quit),
    screen.Command('sotest', [], test_level_supaplex_online),
    screen.Command('verify', [], verify_exit_murphy),
    screen.Command('walls', editor_selection_args, set_selection_outline),
    screen.Command('wls', editor_selection_args, set_selection_outline),
    screen.Command('web', [], open_repository_on_browser),
    screen.Command('repo', [], open_repository_on_browser),
    screen.Command('wtf', [screen.Argument('item', 'int')], display_element_information),
    screen.Command('wth', [screen.Argument('item', 'int')], display_element_information),
    screen.Command('quit', [], quit_level_editor),
    screen.Command('exit', [], quit_level_editor),
    screen.Command('leave', [], quit_level_editor),
    screen.Command('q', [], quit_level_editor),
    screen.Command('reload', [], reload_current_screen),
    screen.Command('rl', [], reload_current_screen)
]

levelset_commands = [
    screen.Command('add', [screen.Argument('path', 'str')], add_level_to_levelset),
    screen.Command('create', [], create_new_level_inside_levelset),
    screen.Command('duplicate', [screen.Argument('level_num', 'int')], duplicate_level_in_levelset),
    screen.Command('dup', [screen.Argument('level_num', 'int')], duplicate_level_in_levelset),
    screen.Command('edit', [screen.Argument('level_num', 'int')], edit_level_from_levelset),
    screen.Command('ed', [screen.Argument('level_num', 'int')], edit_level_from_levelset),
    screen.Command('remove', [screen.Argument('level_num', 'int')], remove_level_from_levelset),
    screen.Command('rm', [screen.Argument('level_num', 'int')], remove_level_from_levelset),
    screen.Command('save', [screen.OptionalArgument('path', '')], save_levelset),
    screen.Command('s', [screen.OptionalArgument('path', '')], save_levelset),
    screen.Command('savequit', [screen.OptionalArgument('path', '')], save_levelset_quit),
    screen.Command('sq', [screen.OptionalArgument('path', '')], save_levelset_quit),
    screen.Command('swap', [screen.Argument('level_a', 'int'), screen.Argument('level_b', 'int')], swap_levels_in_levelset),
    screen.Command('quit', [], quit_to_home_scrn),
    screen.Command('exit', [], quit_to_home_scrn),
    screen.Command('leave', [], quit_to_home_scrn),
    screen.Command('q', [], quit_to_home_scrn),
    screen.Command('reload', [], reload_current_screen),
    screen.Command('rl', [], reload_current_screen),
    screen.Command('web', [], open_repository_on_browser),
    screen.Command('repo', [], open_repository_on_browser)
]

home_scrn.add_several_commands(home_commands)
editor_scrn.add_several_commands(editor_commands)
levelset_scrn.add_several_commands(levelset_commands)

SCREEN = screen.Screen(PARSER.colormap, home_scrn)
home_scrn.register_screen(SCREEN)
editor_scrn.register_screen(SCREEN)
levelset_scrn.register_screen(SCREEN)

SCREEN.change_context(home_scrn)
