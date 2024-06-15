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
# pylint: disable=W0718

CUSTOM_FALSE: tuple[str, str] = ('false', '0')
CUSTOM_TRUE: tuple[str, str] = ('true', '1')
CUSTOM_BOOLS: tuple[str, str, str, str] = CUSTOM_TRUE + CUSTOM_FALSE


class InvalidCommand(Exception): ...
class ArgTypeError(TypeError): ...
class MandatoryArgumentSkipped(Exception): ...


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



class Screen:
    def __init__(self, colormap: dict[str, str | None], initial_context) -> None:
        self._COLORMAP: dict[str, str | None] = colormap
        self._cur_context: Context = initial_context
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

    def change_context(self, new_context):
        self._cur_context = new_context
        self.clear_screen()

        self.write(str(self._cur_context))

    def read_command(self) -> None:
        self.write(f"{self._COLORMAP['COMMAND_BACKGROUND']}{self._COLORMAP['COMMAND_FOREGROUND']}>>> ")
        self.newline()

        command_name = input()

        self._cur_context.remove_state_infoline()

        try:
            command_object: Command = self._cur_context.get_command(command_name)

        except InvalidCommand as e:
            self.clear_screen()
            self.write(f"{self._COLORMAP['ERROR_BACKGROUND']}{self._COLORMAP['ERROR_FOREGROUND']}InvalidCommand - {e}\n\n{self._COLORMAP['RESET_ALL']}{str(self._cur_context)}")
            return

        list_of_args = []

        for argument in command_object.arguments:
            if isinstance(argument, OptionalArgument):
                self.write(f"{self._COLORMAP['ARGUMENT_BACKGROUND']}{self._COLORMAP['ARGUMENT_FOREGROUND']}{argument.name} ({argument.argtype}, defaults to {argument.default_value} - hit ENTER to use this value): ")

                input_arg = input()

                if not input_arg:
                    list_of_args.append(argument.default_value)

                else:
                    list_of_args.append(input_arg)

            elif isinstance(argument, Argument):
                self.write(f"{self._COLORMAP['ARGUMENT_BACKGROUND']}{self._COLORMAP['ARGUMENT_FOREGROUND']}{argument.name} ({argument.argtype}, mandatory): ")

                input_arg = input()

                if not input_arg:
                    self.clear_screen()
                    self.write(f"{self._COLORMAP['ERROR_BACKGROUND']}{self._COLORMAP['ERROR_FOREGROUND']}MissingArgumentForCommand - a value for '{argument.name}' must be given but none was\n\n{self._COLORMAP['RESET_ALL']}{str(self._cur_context)}")
                    return

                else:
                    list_of_args.append(input_arg)

            else:
                self.write(f"{self._COLORMAP['ARGUMENT_BACKGROUND']}{self._COLORMAP['ARGUMENT_FOREGROUND']}{argument.name} (generic argument): ")
                list_of_args.append(input())

        try:
            interpreted_args: list[str | bool | int] = self._cur_context.interpret_command(command_object, list_of_args)[1]

        except ArgTypeError as e:
            self.clear_screen()
            self.write(f"{self._COLORMAP['ERROR_BACKGROUND']}{self._COLORMAP['ERROR_FOREGROUND']}ArgumentRelatedError - {e}\n\n{self._COLORMAP['RESET_ALL']}{str(self._cur_context)}")
            return

        try:
            new_state: str | Context | Any = command_object.call_function(*tuple(interpreted_args))

        except Exception as e:
            self.clear_screen()
            self.write(f"{self._COLORMAP['ERROR_BACKGROUND']}{self._COLORMAP['ERROR_FOREGROUND']}Oops! Something went wrong... - {e}\n\n{self._COLORMAP['RESET_ALL']}{str(self._cur_context)}")
            return

        if isinstance(new_state, str):
            self._cur_context.update_screen(new_state.replace('!/CURRENTRENDERCONTEXTASISNOCHANGE/', str(self._cur_context)))
            return
        
        else:
            self.change_context(new_state)

    
    @property
    def context(self):
        return self._cur_context
    

    builtin_print = print
    print, printlines = write, writelines


SCREEN_INST: Screen | None = None


def setup_screen(scrn: Screen) -> None:
    global SCREEN_INST

    if SCREEN_INST is not None:
        return None

    SCREEN_INST = scrn


class Command:
    def __init__(self, name: str, arguments: list[GenericArgument], function: Callable) -> None:
        self._NAME: str = name
        self._ARGS: list[GenericArgument | Argument | OptionalArgument] = arguments
        
        self._FUNCTION: Callable = function

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
    def __init__(self, name: str, initial_scrn_state: str, commands: list[Command] = None) -> None:
        self._NAME: str = name
        
        if commands is None:
            self._COMMANDS = []
        
        else:
            self._COMMANDS: list[Command] = commands
        
        self._state: str = initial_scrn_state
        
    def add_command(self, command: Command):
        if command in self._COMMANDS:
            raise InvalidCommand('command already exists in this context')
        
        self._COMMANDS.append(command)
        
    def add_several_commands(self, commands: list[Command]):
        for command in commands:
            self.add_command(command)

    def update_state(self, new_state: str) -> None:
        self._state = new_state

    def update_screen(self, update: str) -> None:
        self.update_state(new_state=update)
        SCREEN_INST.clear_screen()
        SCREEN_INST.write(self._state)
    
    def remove_state_infoline(self) -> None:
        self.update_state(new_state=self._state.split('\n', 1)[1])

    def execute_command(self, command: Command, interpreted_args: list[str | bool | int], *args, **kwargs) -> str | Any:
        return command.call_function(*tuple(interpreted_args), *args, **kwargs)

    def get_command(self, command_name: str) -> Command:
        input_command: Command | None = None

        for command in self._COMMANDS:
            if command.name == command_name:
                input_command = command
                break

        if input_command is None:
            raise InvalidCommand(f"such command doesn't exist - use '{random.choice(('help', 'imlost'))}' for more info")

        return input_command

    def interpret_command(self, command: str | Command, given_args: list[str]) -> tuple[Command, list[str | bool | int]]:
        if isinstance(command, str):
            command = self.get_command(command_name=command)

        elif isinstance(command, Command) and command not in self._COMMANDS:
            raise InvalidCommand(f"such command doesn't exist in this context but is a valid Command object - use '{random.choice(('help', 'imlost'))}' for more info")

        interpreted_args: list[str | bool | int] = command.interpret_arguments(given_args=given_args)

        return command, interpreted_args

    @property
    def name(self) -> str:
        return self._NAME

    @property
    def commands(self) -> list[Command]:
        return self._COMMANDS

    def __str__(self) -> str:
        return self._state
