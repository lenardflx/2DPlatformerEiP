import pygame
import json
from time import time

from game.menu.menu_structure import MenuPage, Button
from game.menu.menu_state import MenuState

class WinMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, sound_manager, level):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.cx, self.cy = screen_size[0] // 2, screen_size[1] // 2
        self.button_images = button_images
        self.sound_manager = sound_manager

        self.title = "MISSION COMPLETE"
        self.title_color = (255, 215, 0)

        # Time info
        self.time_taken = round(time() - level.start_time, 2)
        self.time_goal = level.time_to_finish
        self.best_time = None
        self.previous_stars = 0
        self.new_highscore = False

        # Stars
        self.total_stars = 3
        self.stars_earned = 1
        self.evaluate_stars(level)
        self.star_size = 60
        self.star_spacing = 80
        self.star_y = self.cy - 140

        # Animation logic
        self.star_frame = [0 for _ in range(self.total_stars)]
        self.star_appeared = [False for _ in range(self.total_stars)]  # To track sound playback
        self.star_animation_speed = 15
        self.star_delay_per_star = 10
        self.global_frame = 0

        # Load star images
        self.star_image_full = pygame.image.load("assets/menu/star.png").convert_alpha()
        self.star_image_empty = pygame.image.load("assets/menu/star_empty.png").convert_alpha()
        self.star_image_full = pygame.transform.scale(self.star_image_full, (self.star_size, self.star_size))
        self.star_image_empty = pygame.transform.scale(self.star_image_empty, (self.star_size, self.star_size))

        # Buttons
        button_y_start = self.cy + 50
        for i, (name, label) in enumerate([("resume", "Resume"), ("retry", "Retry"), ("menu", "Main Menu")]):
            y = button_y_start + i * 70
            self.add_button(Button(name, button_images[name], (self.cx, y), sound_manager))

    def evaluate_stars(self, level):
        if not len(level.enemies):
            self.stars_earned += 1
        if self.time_taken < level.time_to_finish:
            self.stars_earned += 1

        # Load progress
        path = "data/player_progress.json"
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        level_key = str(level.id)
        prev = data.get(level_key, {})
        self.best_time = prev.get("time")
        self.previous_stars = prev.get("stars", 0)

        # Determine whether to store
        new_best_time = self.best_time is None or self.time_taken < self.best_time
        new_best_stars = self.stars_earned > self.previous_stars
        if new_best_time or new_best_stars:
            data[level_key] = {
                "stars": max(self.stars_earned, self.previous_stars),
                "time": min(self.time_taken, self.best_time) if self.best_time else self.time_taken
            }
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            if new_best_time:
                self.new_highscore = True

    def update(self, mouse_pos):
        self.global_frame += 1
        for i in range(self.stars_earned):  # Only animate earned stars
            delay = i * self.star_delay_per_star
            if self.global_frame > delay and self.star_frame[i] < self.star_animation_speed:
                self.star_frame[i] += 1

                # Play unique sound for each earned star once it finishes animating
                if self.star_frame[i] == self.star_animation_speed and not self.star_appeared[i]:
                    self.star_appeared[i] = True
                    self.sound_manager.play_sfx(f"star_{i + 1}")
        super().update(mouse_pos)

    def render(self, surface):
        # Title
        self.font_manager.render(surface, self.title, (self.cx, 30), 48, self.title_color, align_center=True)

        # Stars
        for i in range(self.total_stars):
            x = self.cx + (i - 1) * self.star_spacing
            if i < self.stars_earned:
                progress = self.star_frame[i] / self.star_animation_speed
                scale = 0.5 + 0.5 * progress
                size = int(self.star_size * scale)
                star = pygame.transform.scale(self.star_image_full, (size, size))
                surface.blit(star, (x - size // 2, self.star_y - size // 2))
            else:
                surface.blit(self.star_image_empty, (x - self.star_size // 2, self.star_y - self.star_size // 2))

        # Score Info
        info_y = self.star_y + self.star_size
        spacing = 24
        self.font_manager.render(surface, f"Your Time: {self.time_taken}s", (self.cx, info_y), 22, (255, 255, 255), align_center=True)
        self.font_manager.render(surface, f"Goal Time: {self.time_goal}s", (self.cx, info_y + spacing), 20, (180, 180, 180), align_center=True)

        if self.best_time is not None:
            self.font_manager.render(surface, f"Best Time: {self.best_time}s", (self.cx, info_y + spacing * 2), 20, (200, 255, 200), align_center=True)
        if self.new_highscore:
            self.font_manager.render(surface, "New Highscore!", (self.cx, info_y + spacing * 3), 24, (255, 255, 0), align_center=True)

        # Buttons
        super().render(surface)

    def handle_event(self, event, engine, mouse_pos):
        for button in self.buttons:
            if button.is_clicked(event, mouse_pos):
                if button.name == "resume":
                    engine.start_game()
                    engine.is_playing = True
                    engine.menu.close_menu(engine)
                elif button.name == "retry":
                    engine.load_level(engine.current_level)
                    engine.is_playing = True
                    engine.menu.close_menu(engine)
                elif button.name == "menu":
                    engine.is_playing = False
                    engine.menu.open_menu(MenuState.MAIN, engine)
