import json
import pygame

class Controls:
    def __init__(self):
        self.controls = {}
        self.load_controls()

    def load_controls(self):
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
        keys = pygame.key.get_pressed()
        return any(keys[key] for key in self.controls.get(action, []))

    def reload_controls(self):
        self.load_controls()
