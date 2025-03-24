import json
import os
import pygame


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.config_path = "data/settings.json"
        self.default_settings = {
            "controls": {
                "move_left": [pygame.K_LEFT, pygame.K_a],
                "move_right": [pygame.K_RIGHT, pygame.K_d],
                "jump": [pygame.K_SPACE, pygame.K_w],
                "menu": [pygame.K_ESCAPE, None],
                "gravity_inverse": [pygame.K_g, None]
            },
            "volume": {
                "music": 0.5,
                "sfx": 0.8
            }
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as file:
                    data = json.load(file)
                    # Fill missing keys and ensure all controls have 2 slots
                    settings = self.default_settings.copy()
                    settings["volume"].update(data.get("volume", {}))

                    settings["controls"] = {}
                    for action, default_keys in self.default_settings["controls"].items():
                        raw_keys = data.get("controls", {}).get(action, default_keys)
                        padded = (raw_keys + [None, None])[:2]
                        settings["controls"][action] = [
                            pygame.key.key_code(k) if isinstance(k, str) and k is not None else k
                            for k in padded
                        ]

                    return settings

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"⚠️ Error loading settings: {e} — Reverting to defaults.")
                return self.default_settings.copy()
        else:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            self.save_settings()
            return self.default_settings.copy()

    def save_settings(self):
        settings_to_save = {
            "volume": self.settings.get("volume", {}).copy(),
            "controls": {}
        }

        for action, keys in self.settings["controls"].items():
            settings_to_save["controls"][action] = [
                pygame.key.name(k) if k is not None else None for k in (keys + [None, None])[:2]
            ]

        with open(self.config_path, "w") as file:
            json.dump(settings_to_save, file, indent=4)

    def get(self, section, key=None):
        if key:
            return self.settings.get(section, {}).get(key)
        return self.settings.get(section, {})

    def set(self, section, key, value):
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save_settings()

    def get_controls(self, action):
        return self.settings["controls"].get(action, [None, None])

    def set_control(self, action, index, key):
        if action not in self.settings["controls"]:
            self.settings["controls"][action] = [None, None]
        while len(self.settings["controls"][action]) < 2:
            self.settings["controls"][action].append(None)
        self.settings["controls"][action][index] = key
        self.save_settings()
