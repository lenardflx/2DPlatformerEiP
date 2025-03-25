import pygame
import json

from game.menu.menu_structure import MenuPage, Button
from game.menu.menu_state import MenuState
from game.menu.scroll_handler import ScrollHandler


class LevelsMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, sound_manager, levels_data):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.cx = screen_size[0] // 2
        self.line_height = 64
        self.padding_top = 30
        self.background_color = (10, 10, 10)

        self.levels_data = levels_data
        self.progress = self.load_progress()
        self.unlocked_levels = self.get_unlocked_levels()

        self.scroll = ScrollHandler(screen_size, fade_color=(10, 10, 10, 255))
        self.entries = [(int(level_id), level_info.get("title", "Unknown"))
                        for level_id, level_info in sorted(levels_data.items(), key=lambda x: int(x[0]))]
        self.content_height = self.padding_top + len(self.entries) * self.line_height
        self.scroll.update_max_scroll(self.content_height)

        self.hovered_index = -1
        self.back_button = Button("back", button_images["back"], (self.cx, screen_size[1] - 80), sound_manager)

    def get_unlocked_levels(self):
        unlocked = set()
        for key in self.progress.keys():
            try:
                level_id = int(key)
                unlocked.add(level_id)
                unlocked.add(level_id + 1)
            except ValueError:
                continue
        return unlocked

    @staticmethod
    def load_progress():
        with open("data/player_progress.json", "r") as f:
            return json.load(f)


    def handle_event(self, event, engine, mouse_pos):
        if self.back_button.is_clicked(event, mouse_pos):
            engine.menu.set_active_page(MenuState.MAIN)
            return

        self.scroll.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self.get_hovered_index(mouse_pos)
            if 0 <= index < len(self.entries):
                level_id, _ = self.entries[index]
                if level_id not in self.unlocked_levels:
                    self.sound_manager.play_sfx("error")
                    return
                self.sound_manager.play_sfx("button_click")
                engine.start_game()
                engine.load_levels_data(level_id)

    def update(self, mouse_pos):
        self.scroll.clamp_scroll()
        self.hovered_index = self.get_hovered_index(mouse_pos)
        self.back_button.update(mouse_pos)

    def get_hovered_index(self, mouse_pos):
        _, my = mouse_pos
        base_y = self.padding_top - self.scroll.scroll_offset + self.scroll.scroll_area_top
        for i in range(len(self.entries)):
            entry_y = base_y + i * self.line_height
            if entry_y <= my <= entry_y + self.line_height:
                return i
        return -1

    def render(self, surface):
        surface.fill(self.background_color)

        # Title
        self.font_manager.render(
            surface, "Select Level", (self.cx, 60), size=40,
            align_center=True, color=(255, 255, 255)
        )

        # Scrollable area
        scroll_surf = pygame.Surface((self.screen_size[0], self.scroll.scroll_area_height), pygame.SRCALPHA)
        base_y = self.padding_top - self.scroll.scroll_offset

        for i, (level_id, title) in enumerate(self.entries):
            y = base_y + i * self.line_height
            if 0 <= y < self.scroll.scroll_area_height:
                is_hovered = (i == self.hovered_index)
                unlocked = level_id in self.unlocked_levels
                stats = self.progress.get(str(level_id), {})
                stars = stats.get("stars", 0)
                best_time = stats.get("time", None)

                # Left: Title
                title_color = (220, 220, 220) if unlocked else (100, 100, 100)
                title_text = f"{level_id}. {title}"
                if is_hovered and unlocked:
                    title_color = (255, 255, 150)
                    title_text = "> " + title_text
                else:
                    title_text = "  " + title_text
                self.font_manager.render(
                    scroll_surf, title_text, (60, y + 6),
                    size=22, color=title_color
                )

                # Center: Stars as x/3
                stars_color = (255, 215, 0) if unlocked else (80, 80, 80)
                stars_text = f"{stars}/3"
                if is_hovered and unlocked:
                    stars_color = (255, 255, 150)
                self.font_manager.render(
                    scroll_surf, stars_text, (self.cx, y + 6),
                    size=20, align_center=True, color=stars_color
                )

                # Right: Best Time
                if not best_time:
                    time_text = "N/A"
                else:
                    time_text = f"{best_time:.2f}"
                time_color = (200, 255, 200) if unlocked else (80, 80, 80)
                if is_hovered and unlocked:
                    time_color = (255, 255, 150)
                    time_text = time_text + " <"
                else:
                    time_text = time_text + "  "
                self.font_manager.render(
                    scroll_surf, time_text, (self.screen_size[0] - 80, y + 6),
                    size=20, align_center=True, color=time_color
                )

        surface.blit(scroll_surf, (0, self.scroll.scroll_area_top))
        self.scroll.render_scroll_fade(surface)

        # Hint
        self.font_manager.render(
            surface, "Scroll to navigate, click to play", (self.cx, self.screen_size[1] - 40),
            size=18, align_center=True, color=(120, 120, 120)
        )
        self.back_button.render(surface)
