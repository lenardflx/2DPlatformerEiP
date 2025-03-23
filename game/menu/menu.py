# game/menu/menu.py
import json
import os
import pygame

from game.menu.menu_state import MenuState
from game.menu.main_menu import MainMenu
from game.menu.levels_menu import LevelsMenu
from game.menu.pause_menu import PauseMenu
from game.menu.death_menu import DeathMenu
from game.menu.settings_menu import SettingsMenu


class Menu:
    def __init__(self, screen_size, controls, levels_data, font_manager, sound_manager):
        self.controls = controls
        self.levels_data = levels_data
        self.active_type = None
        self.screen_size = screen_size
        self.current_page = None

        self.font_manager = font_manager
        self.sound_manager = sound_manager

        self.button_images = self.load_button_images()
        self.set_active_page(MenuState.MAIN)

        self.last_frame = None
        self.back_redirect = MenuState.MAIN

    @staticmethod
    def load_button_images():
        with open("assets/menu/menu.json") as f:
            data = json.load(f)

        buttons = {}
        for key, entry in data.items():
            img = pygame.image.load(os.path.join("assets/menu",entry["image"])).convert_alpha()
            w = entry["frame_width"]
            h = img.get_height()
            frames = [img.subsurface(pygame.Rect(i * w, 0, w, h)) for i in range(img.get_width() // w)]
            buttons[key] = {
                "idle": frames[0],
                "hover": frames[1:] if len(frames) > 1 else frames[0]
            }
        return buttons

    def open_menu(self, menu_type, engine):
        """Opens a menu, stores the current frame and pauses game if needed."""
        if engine.is_playing:
            self.last_frame = engine.scaled_surface.copy()
            engine.is_playing = False
            self.back_redirect = MenuState.PAUSE
        else:
            self.back_redirect = MenuState.MAIN  # Fallback when opened from non-play mode

        self.set_active_page(menu_type)

    def close_menu(self, engine):
        """Closes the menu and resumes the game if it was paused."""
        self.active_type = MenuState.NONE
        self.current_page = None
        self.last_frame = None
        engine.is_playing = True

    def toggle_menu(self, menu_type, engine):
        if self.active_type == MenuState.NONE:
            self.open_menu(menu_type, engine)
        else:
            self.close_menu(engine)

    def set_active_page(self, menu_state):
        """Sets the active page based on the given menu state. Assumes state logic is handled externally."""
        self.active_type = menu_state

        if menu_state == MenuState.MAIN:
            self.current_page = MainMenu(self.screen_size, self.button_images, self.font_manager, self.sound_manager)
        elif menu_state == MenuState.LEVELS:
            self.current_page = LevelsMenu(
                self.screen_size, self.button_images, self.font_manager, self.sound_manager, self.levels_data
            )
        elif menu_state == MenuState.PAUSE:
            self.current_page = PauseMenu(self.screen_size, self.button_images, self.font_manager, self.sound_manager)
        elif menu_state == MenuState.DEATH:
            self.current_page = DeathMenu(self.screen_size, self.button_images, self.font_manager, self.sound_manager)
        elif menu_state == MenuState.SETTINGS:
            self.current_page = SettingsMenu(
                self.screen_size, self.button_images, self.font_manager, self.controls, self.sound_manager
            )

    def handle_event(self, event, engine):
        if self.active_type == MenuState.NONE:
            return

        mouse_pos = engine.get_scaled_mouse()
        self.current_page.handle_event(event, engine, mouse_pos)

    def render(self, surface, engine):
        if self.active_type == MenuState.NONE:
            return

        mouse_pos = engine.get_scaled_mouse()

        # Background from last frame
        if self.last_frame:
            surface.blit(self.last_frame, (0, 0))

        # Overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

        # Actual menu page
        self.current_page.update(mouse_pos)
        self.current_page.render(surface)

