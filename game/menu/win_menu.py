import pygame
import json
import os
from time import time

from game.menu.menu_structure import MenuPage, Button
from game.menu.menu_state import MenuState

class WinMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, sound_manager, level):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.cx, self.cy = screen_size[0] // 2, screen_size[1] // 2
        self.button_images = button_images

        self.title = "MISSION COMPLETE"
        self.title_color = (255, 215, 0)

        # Star setup
        self.stars_earned = 1
        self.evaluate_stars(level)
        self.star_size = 60
        self.star_spacing = 80
        self.star_y = self.cy - 50
        self.star_animation_time = 0
        self.star_scale = 1.0

        # Load star image
        self.star_image = pygame.image.load("assets/menu/star.png").convert_alpha()
        self.star_image = pygame.transform.scale(self.star_image, (self.star_size, self.star_size))

        # Buttons
        spacing = 80
        options = [
            ("resume", "Resume", self.cy + spacing),
            ("menu", "Menu", self.cy + 2 * spacing)
        ]
        for name, display_name, y in options:
            self.add_button(Button(name, button_images[name], (self.cx, y), sound_manager))

    def evaluate_stars(self, level):
        """Evaluates which stars were earned based on level stats."""
        # Star 2: all enemies defeated
        print(len(level.enemies))
        if not len(level.enemies):
            self.stars_earned += 1

        # Star 3: beat within time limit
        print(time() - level.start_time, level.time_to_finish)
        if time() - level.start_time < level.time_to_finish:
            self.stars_earned += 1

        self.store_progress(level)

    def store_progress(self, level):
        """Stores progress to a JSON file."""
        path = "data/player_progress.json"
        with open(path, "r") as f:
            data = json.load(f)

        data[str(level.id)] = {
            "stars": self.stars_earned,
            "time": round(time() - level.start_time, 2)
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def update(self, mouse_pos):
        self.star_animation_time += 0.05
        self.star_scale = 1.0 + 0.1 * abs(pygame.math.Vector2().rotate(self.star_animation_time * 360).y)
        super().update(mouse_pos)

    def render(self, surface):
        # Title
        self.font_manager.render(
            surface=surface,
            text=self.title,
            position=(self.cx, 100),
            size=48,
            color=self.title_color,
            align_center=True
        )

        # Stars
        stars_earned = self.stars_earned
        for i in range(3):
            x = self.cx + (i - 1) * self.star_spacing
            print(i, stars_earned)
            if stars_earned:
                star = pygame.transform.scale(self.star_image, (int(self.star_size * self.star_scale), int(self.star_size * self.star_scale)))
                surface.blit(star, (x, self.star_y))
                stars_earned -= 1
            else:
                pygame.draw.rect(surface, (50, 50, 50), (x, self.star_y, self.star_size, self.star_size))

        # Buttons
        super().render(surface)

    def handle_event(self, event, engine, mouse_pos):
        for button in self.buttons:
            if button.is_clicked(event, mouse_pos):
                if button.name == "resume":
                    engine.load_level(engine.next_level)
                    engine.is_playing = True
                    engine.menu.close_menu(engine)
                elif button.name == "menu":
                    engine.is_playing = False
                    engine.menu.open_menu(MenuState.MAIN, engine)
