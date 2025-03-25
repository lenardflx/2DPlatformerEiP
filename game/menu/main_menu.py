import pygame
import sys

from core.game_data import get_game_data
from game.menu.menu_structure import MenuPage, Button
from game.menu.menu_state import MenuState
from game.background import Background


class MainMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, sound_manager):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.cx, self.cy = screen_size[0] // 2, screen_size[1] // 2
        self.button_images = button_images
        self.title = get_game_data("game_title")
        self.credits = f"Made by {get_game_data('contributors')}"
        self.title_color = (255, 233, 71)

        # Load scrolling background layers (static + scroll types)
        self.backgrounds = []
        bg_data = get_game_data("main_menu_background")
        for layer in bg_data[::-1]:  # Back to front
            self.backgrounds.append(Background(layer))

        spacing = 70
        button_names = ["play", "levels", "options", "exit"]
        for i, name in enumerate(button_names):
            y = self.cy - spacing + i * spacing
            self.add_button(Button(name, button_images[name], (self.cx, y), sound_manager))

    def render(self, surface):
        # Background layers (static or scroll)
        for bg in self.backgrounds:
            bg.render(surface, camera=None)  # No camera in menu

        # Title
        self.font_manager.render(
            text=self.title,
            surface=surface,
            position=(self.cx, 70),
            size=48,
            color=self.title_color,
            align_center=True
        )

        # Buttons
        super().render(surface)

        # Credits in bottom right
        self.font_manager.render(
            text=self.credits,
            surface=surface,
            position=(self.screen_size[0] - 20, self.screen_size[1] - 20),
            size=18,
            color=(180, 180, 180),
            align_right=True
        )

    def update(self, mouse_pos):
        for bg in self.backgrounds:
            if bg.type == "scroll":
                bg.offset += bg.speed
        super().update(mouse_pos)

    def handle_event(self, event, engine, mouse_pos):
        for button in self.buttons:
            if button.is_clicked(event, mouse_pos):
                if button.name == "play":
                    engine.menu.back_redirect = MenuState.PAUSE
                    engine.start_game()
                elif button.name == "exit":
                    pygame.quit()
                    sys.exit()
                elif button.name == "options":
                    engine.menu.set_active_page(MenuState.SETTINGS)
                elif button.name == "levels":
                    engine.menu.set_active_page(MenuState.LEVELS)
