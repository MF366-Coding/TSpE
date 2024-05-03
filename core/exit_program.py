# exit_program.py

"""
Just exits TSpE the safe way, I guess?
"""

from typing import Any
from core import settings
import sys


def leave_program(parser: settings.SettingsParser, code: Any = None):
    parser.save_settings()
    sys.exit(code)
