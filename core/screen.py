# screen.py

"""
'screen' component

The screen component controls the scopes, what appears on screen and the commands.
"""

import sys
from colorama import Fore, Back

# pylint: disable=W0123

class Scope:
    def __init__(self, name: str):           
        self._NAME = name
        
    @property
    def name(self) -> str:
        return self._NAME


scopes = [
    Scope('START')
]

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


class CommandDB:
    '''
    TODO
    '''
    
    ...


class Screen:
    def __init__(self, data: dict[str, str], colormap: dict[str, str | None]) -> None:
        self._COLORMAP = colormap
        
        self.pretty_ascii(data.get('ascii', []))
        
        self.reset()
        self.newline()
        
        self.write(f"{colormap['TITLE']}{data['name']}{colormap['RESET']} by {colormap['AUTHOR']}{data['author']}\n")
        self.reset()
        
        self.write(f"{colormap['DESCRIPTION']}{data.get('description', '')}\n{data.get('copyright', '')}")
        self.reset()
        self.newline(2)
    
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
            
    def read_command(self, commands: CommandDB):
        '''
        TODO
        '''
        
        command = input(f"{self._COLORMAP['COMMAND_START']}>>> {self._COLORMAP['COMMAND_INSERT']}")
        
            
    outside_print = print
    print, printlines = write, writelines
        