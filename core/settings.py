import json


def get_settings(path: str) -> dict[str, dict[str, str] | bool]:
    with open(path, 'r', encoding='utf-8') as f:
        settings = json.load(f)
        
    return settings


def save_settings(path: str, settings: dict[str, dict[str, str] | bool]):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)


def parse_colormap(settings: dict[str, dict[str, str] | bool]) -> dict[str, str]:
    return settings['colormap']


def parse_testers(settings: dict[str, dict[str, str] | bool]) -> dict[str, str]:
    return settings['testProviders']


def parse_tags(settings: dict[str, dict[str, str] | bool]) -> dict[str, str]:
    return settings['tags']


def parse_reminders(settings: dict[str, dict[str, str] | bool]) -> dict[str, str]:
    return settings['reminders']


# [!!] VERY Experimental feature (might not go thru in final version)
def parse_user_commands(settings: dict[str, dict[str, str] | bool]) -> dict[str, str]:
    return settings['userCommands']
