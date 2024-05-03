import json


class SettingsParser:
    def __init__(self, path: str) -> None:
        self._path = path
        self._settings: dict[str, dict[str, str] | bool] | None = None
        self._get_settings()

    def _get_settings(self):
        with open(self._path, 'r', encoding='utf-8') as f:
            self._settings = json.load(f)

    def save_settings(self):
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(self._settings, f, indent=4)

    def save_reload(self):
        self.save_settings()
        self._get_settings()

    def force_reload(self, path: str | None = None):
        self._path = path if path is not None else self._path
        self._get_settings()

    @property
    def settings(self) -> dict[str, dict[str, str] | bool]:
        return self._settings

    @property
    def colormap(self) -> dict[str, str]:
        return self._settings['colormap']

    @property
    def testers(self) -> dict[str, str]:
        return self._settings['testProviders']

    @property
    def tags(self) -> dict[str, str]:
        return self._settings['tags']

    @property
    def allow_eval(self) -> bool:
        return self._settings['allowEvaluate']

    @property
    def allow_del(self) -> bool:
        return self._settings['allowDelete']

    @property
    def online_help(self) -> bool:
        return self._settings['useOnlineHelp']

    @property
    def logging(self) -> bool:
        return self._settings['logging']

    test_providers: property = testers
