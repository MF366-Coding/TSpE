# screen.py

"""
'screen' component

The screen component controls the scopes, what appears on screen and the commands.
"""

import os
import sys
import time
import random
from typing import Callable, Any
from colorama import Fore

# pylint: disable=W0123
# pylint: disable=W0603
# pylint: disable=W0707

CUSTOM_FALSE: tuple[str] = ('false', '0')
CUSTOM_TRUE: tuple[str] = ('true', '1')
CUSTOM_BOOLS = CUSTOM_TRUE + CUSTOM_FALSE


class InvalidCommand(Exception): ...
class TooManyArguments(Exception): ...
class ArgTypeError(TypeError): ...
class CommandHasBeenBuilt(Exception): ...


class Screen:
    '''
    TODO
    '''
    
    def __init__(self, data: dict[str, str], colormap: dict[str, str | None], initial_context) -> None:
        self._COLORMAP: dict[str, str | None] = colormap
        self._DATA: dict[str, str] = data
        self._CONTEXT = initial_context
        self._last_cleared: float = time.time()

    def newline(self, count: int = 1):
        self.write('\n' * count)

    def reset(self):
        self.write(self._COLORMAP.get('RESET', Fore.RESET))

    def write(self, __s: str, __stdout: bool = True):
        __outputter = sys.stdout

        if not __stdout:
            __outputter = sys.stderr

        return __outputter.write(__s)

    def writelines(self, __iterable: list[str], __stdout: bool = True):
        __outputter = sys.stdout

        if not __stdout:
            __outputter = sys.stderr

        __outputter.writelines(__iterable)

    def pretty_ascii(self, __table: list[str]):
        for index, line in enumerate(__table, 0):
            if index % 2 == 0:
                self.write(self._COLORMAP['ASCII_PRIMARY'], True)

            else:
                self.write(self._COLORMAP['ASCII_SECONDARY'], True)

            self.write(f"{line}\n", True)

    def clear_screen(self, *_, **options) -> int:
        if options.get('count_time', True):
            self._last_cleared = time.time()

        return os.system('cls' if sys.platform == 'win32' else 'clear')

    builtin_print = print
    print, printlines = write, writelines


SCREEN_INST: Screen | None = None


def setup_screen(scrn: Screen) -> None:
    global SCREEN_INST

    if SCREEN_INST is not None:
        return None

    SCREEN_INST = scrn


class GenericArgument:
    def __init__(self, name: str) -> None:
        self._NAME: str = name

    @property
    def name(self) -> str:
        return self._NAME


class Argument(GenericArgument):
    def __init__(self, name: str, argtype: str = 'str') -> None:
        super().__init__(name)

        if argtype not in ('str', 'int', 'bool'):
            argtype = 'str'

        self._TYPE: str = argtype

    @property
    def argtype(self) -> str:
        return self._TYPE

    @property
    def argtype_as_pytype(self) -> type[bool] | type[int] | type[str] | None:
        match self._TYPE:
            case 'bool':
                return bool

            case 'int':
                return int

            case 'str':
                return str

        return None


class OptionalArgument(GenericArgument):
    def __init__(self, name: str, default_value: object, argtype: str = 'str') -> None:
        super().__init__(name)

        if argtype not in ('str', 'int', 'bool'):
            argtype = 'str'

        self._TYPE: str = argtype

        if not isinstance(default_value, self.argtype_as_pytype()):
            raise TypeError('default value does not match argument type')

        self._DEFAULT_VALUE: object = default_value

    @property
    def argtype(self) -> str:
        return self._TYPE

    @property
    def argtype_as_pytype(self) -> type[bool] | type[int] | type[str] | None:
        match self._TYPE:
            case 'bool':
                return bool

            case 'int':
                return int

            case 'str':
                return str

        return None

    @property
    def default_value(self) -> object:
        return self._DEFAULT_VALUE


class Command:
    def __init__(self, name: str, arguments: list[GenericArgument], function: Callable) -> None:
        self._NAME: str = name
        self._ARGS: list[GenericArgument | Argument | OptionalArgument] = arguments
        self._FUNCTION = function
        
    def call_function(self, *args, **kwargs) -> str | Any:
        return self._FUNCTION(*args, **kwargs)
    
    def interpret_arguments(self, given_args: list[str]) -> list[str | bool | int]:
        arg_list: list[str | bool | int] = []
        
        for index, given_arg in enumerate(given_args, 0):
            if isinstance(self._ARGS[index], OptionalArgument) and not given_arg:
                arg_list.append(self._ARGS[index].default_value)
                continue
                
            match self._ARGS[index].argtype:
                case "bool":
                    if given_arg.lower().strip() in CUSTOM_TRUE:
                        arg_list.append(True)
                        
                    elif given_arg.lower().strip() in CUSTOM_FALSE:
                        arg_list.append(False)
                        
                    else:
                        raise ArgTypeError(f'expected boolean value but got "{given_arg.lower().strip()}"')
                    
                case 'int':
                    if given_arg.strip().isdigit():
                        arg_list.append(int(given_arg))
                        
                    else:
                        raise ArgTypeError(f'expected integer value but got "{given_arg.strip()}"')
                    
                case _:
                    arg_list.append(given_arg)
                    
        return arg_list
    
    @property
    def name(self) -> str:
        return self._NAME
    
    @property
    def arguments(self) -> list[GenericArgument | Argument | OptionalArgument]:
        return self._ARGS
    
    @property
    def function(self) -> Callable:
        return self._FUNCTION


class Context:
    def __init__(self, name: str, commands: list[Command], initial_scrn_state: str) -> None:
        self._NAME: str = name
        self._COMMANDS: list[Command] = commands
        self._state: str = initial_scrn_state
    
    def update_state(self, new_state: str):
        self._state = new_state
    
    def update_screen(self, update: str):
        self.update_state(update)
        SCREEN_INST.clear_screen()
        SCREEN_INST.write(self._state)
    
    def execute_command(self, command: Command, interpreted_args: list[str | bool | int], *args, **kwargs) -> str | Any:
        return command.call_function(*tuple(interpreted_args), *args, **kwargs)
     
    def interpret_command(self, command_name: str, given_args: list[str]) -> tuple[Command, list[str | bool | int]]:
        input_command: Command | None = None
        
        for command in self._COMMANDS:
            if command.name == command_name:
                input_command = command
                break
        
        if input_command is None:
            raise InvalidCommand(f"such command doesn't exist - use '{random.choice(('help', 'imlost'))}' for more info")
        
        interpreted_args: list[str | bool | int] = input_command.interpret_arguments(given_args)
        
        return input_command, interpreted_args
    
    @property
    def name(self) -> str:
        return self._NAME
    
    @property
    def commands(self) -> list[Command]:
        return self._COMMANDS
    
    def __str__(self) -> str:
        return self._state
