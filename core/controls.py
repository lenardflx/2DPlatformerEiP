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

        for action in self.controls.keys():
            while len(self.controls[action]) < 2:
                self.controls[action].append(None)

    def is_action_active(self, action):
        """Returns True if any of the keys bound to the action are pressed."""
        keys = pygame.key.get_pressed()
        return any(keys[key] for key in self.controls.get(action, []) if key is not None)

    def bind_key(self, action, new_key):
        """Rebinds a key to an action."""
        if action in self.controls:
            if new_key in self.controls[action]:
                return  # Avoid duplicate bindings

            if len(self.controls[action]) >= 2:
                self.controls[action][0] = new_key  # Replace the first key
            else:
                self.controls[action].append(new_key)  # Add key binding
        else:
            self.controls[action] = [new_key]  # Create a new binding

        self.save_controls()

    def save_controls(self):
        """Saves control settings to data/settings.json."""
        with open("data/settings.json", "r") as file:
            data = json.load(file)

        data["controls"] = {
            action: [pygame.key.name(key) for key in keys]
            for action, keys in self.controls.items()
        }

        with open("data/settings.json", "w") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def convert_key_to_pygame(key_name):
        """Converts key name from JSON to pygame key code."""
        return getattr(pygame, f"K_{key_name}", pygame.K_UNKNOWN)