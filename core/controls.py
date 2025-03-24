import pygame
from core.settings import Settings

class Controls:
    def __init__(self):
        self.settings = Settings()
        self.controls = self.settings.get("controls")

    def bind_key(self, action, new_key, index=0):
        """Rebinds a key to an action at a specific index."""
        # Check for duplicates across all actions
        for other_action, keys in self.controls.items():
            if other_action != action and new_key in keys:
                keys[keys.index(new_key)] = None  # Remove from other action
        self.settings.set_control(action, index, new_key)
        self.controls = self.settings.get("controls")  # Refresh local copy

    def is_action_active(self, action):
        """Returns True if any of the keys bound to the action are pressed."""
        keys = pygame.key.get_pressed()
        return any(keys[key] for key in self.controls.get(action, []) if key is not None)

    def get_keys(self, action):
        """Returns the list of keys for an action."""
        return self.controls.get(action, [None, None])

    @staticmethod
    def convert_key_to_pygame(key_name):
        """Converts key name to pygame key code."""
        try:
            return pygame.key.key_code(key_name.lower())
        except ValueError:
            return pygame.K_UNKNOWN