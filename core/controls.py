import json
import pygame
import os


class Controls:
    def __init__(self, config_path="data/settings.json"):
        self.config_path = config_path
        self.controls = {}
        self.load_controls()

    def load_controls(self):
        """Loads control settings from data/settings.json, with defaults if needed."""
        default_controls = {
            "move_left": [pygame.K_LEFT, pygame.K_a],
            "move_right": [pygame.K_RIGHT, pygame.K_d],
            "jump": [pygame.K_SPACE, pygame.K_w],
            "menu": [pygame.K_ESCAPE],
            "gravity_inverse": [pygame.K_g]
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as file:
                    data = json.load(file)
                    controls_data = data.get("controls", {})
                    self.controls = {}
                    for action, keys in controls_data.items():
                        self.controls[action] = []
                        for key in keys:
                            if key is not None:  # Handle None explicitly
                                # Convert key name to pygame key code
                                key_code = self.convert_key_to_pygame(key)
                                self.controls[action].append(key_code)
                            else:
                                self.controls[action].append(None)
                        # Ensure at least 2 slots per action
                        while len(self.controls[action]) < 2:
                            self.controls[action].append(None)
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"Error loading controls: {e}. Using defaults.")
                self.controls = default_controls
                self.save_controls()
        else:
            self.controls = default_controls
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            self.save_controls()

    def save_controls(self):
        """Saves control settings to data/settings.json."""
        # Read existing data to preserve other settings
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as file:
                data = json.load(file)
        else:
            data = {}

        # Update controls section
        data["controls"] = {
            action: [pygame.key.name(key) if key is not None else None
                     for key in keys]
            for action, keys in self.controls.items()
        }

        # Write back to file
        with open(self.config_path, "w") as file:
            json.dump(data, file, indent=4)

    def bind_key(self, action, new_key, index=0):
        """Rebinds a key to an action at a specific index."""
        if action not in self.controls:
            self.controls[action] = [None, None]  # Initialize with 2 slots

        # Ensure the list is long enough
        while len(self.controls[action]) <= index:
            self.controls[action].append(None)

        # Check for duplicates across all actions (optional)
        for other_action, keys in self.controls.items():
            if other_action != action and new_key in keys:
                keys[keys.index(new_key)] = None  # Remove from other action

        # Set the new key at the specified index
        self.controls[action][index] = new_key
        self.save_controls()

    def is_action_active(self, action):
        """Returns True if any of the keys bound to the action are pressed."""
        keys = pygame.key.get_pressed()
        return any(keys[key] for key in self.controls.get(action, []) if key is not None)

    @staticmethod
    def convert_key_to_pygame(key_name):
        """Converts key name from JSON to pygame key code."""
        try:
            return pygame.key.key_code(key_name.lower())  # Use key_code for better compatibility
        except ValueError:
            return pygame.K_UNKNOWN

    def get_keys(self, action):
        """Returns the list of keys for an action."""
        return self.controls.get(action, [None, None])