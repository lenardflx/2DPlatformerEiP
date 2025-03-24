import pygame
import sys

from core.game_data import get_game_data
from game.menu.menu_structure import MenuPage, Button
from game.menu.menu_state import MenuState


class MainMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, sound_manager):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.cx, self.cy = screen_size[0] // 2, screen_size[1] // 2
        self.button_images = button_images
        self.title = get_game_data("game_title")
        self.credits = f"Made by {get_game_data("contributors")}"
        self.title_color = (255, 255, 255)
        self.background = pygame.image.load("assets/menu/menu_bg.png").convert()

        scale =  (int(self.background.get_width() * screen_size[1] / self.background.get_height()), screen_size[1])
        self.background = pygame.transform.scale(self.background, scale)

        spacing = 80
        button_names = ["play", "levels", "options", "exit"]
        for i, name in enumerate(button_names):
            y = self.cy - spacing + i * spacing
            self.add_button(Button(name, button_images[name], (self.cx, y), sound_manager))

    def render(self, surface):
        # Background
        surface.blit(self.background, (0, 0))

        # Title at top center
        self.font_manager.render(
            text=self.title,
            surface=surface,
            position=(self.cx, 70),
            size=48,
            color=self.title_color,
            align_center=True
        )

        # Render all buttons
        super().render(surface)

        # Credits in bottom right corner
        self.font_manager.render(
            text=self.credits,
            surface=surface,
            position=(self.screen_size[0] - 20, self.screen_size[1] - 20),
            size=18,
            color=(180, 180, 180),
            align_right=True
        )

    def handle_event(self, event, engine, mouse_pos):
        for button in self.buttons:
            if button.is_clicked(event, mouse_pos):
                if button.name == "play":
                    engine.start_game()
                elif button.name == "exit":
                    pygame.quit()
                    sys.exit()
                elif button.name == "options":
                    engine.menu.set_active_page(MenuState.SETTINGS)
                elif button.name == "levels":
                    engine.menu.set_active_page(MenuState.LEVELS)
