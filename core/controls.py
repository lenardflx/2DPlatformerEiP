import json
import pygame

class Controls:
    def __init__(self):
        self.controls = {}
        self.load_controls()

    def load_controls(self):
        """Loads control settings from data/settings.json."""
        with open("data/settings.json", "r") as file:
            data = json.load(file)
            self.controls = {
                action: [
                    getattr(pygame, f"K_{key.lower()}") if len(key) == 1 else getattr(pygame, f"K_{key.upper()}")
                    for key in keys
                ]
                for action, keys in data["controls"].items()
            }

    def is_action_active(self, action):
        """Returns True if any of the keys bound to the action are pressed."""
        keys = pygame.key.get_pressed()
        return any(keys[key] for key in self.controls.get(action, []))

    def reload_controls(self):
        """Reloads control settings"""
        self.load_controls()

    def bind_key(self, action, key, index):
        """Binds a key to an action"""
        self.controls[action][index] = key
        self.save_controls()

    def save_controls(self):
        """Saves control settings to data/settings.json."""
        with open("data/settings.json", "r") as file:
            data = json.load(file)
            data["controls"] = {
                action: [
                    key if isinstance(key, str) else key.name
                    for key in keys
                ]
                for action, keys in self.controls.items()
            }
        with open("data/settings.json", "w") as file:
            json.dump(data, file, indent=4)