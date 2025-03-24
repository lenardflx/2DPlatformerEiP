import pygame
from game.menu.menu_structure import MenuPage, Button
from game.menu.menu_state import MenuState
from game.menu.scroll_handler import ScrollHandler


class LevelsMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, sound_manager, levels_data):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.sound_manager = sound_manager
        self.cx = screen_size[0] // 2
        self.line_height = 50
        self.padding_top = 20  # Reduced to start near top
        self.background_color = (10, 10, 10)

        # Scroll setup
        self.scroll = ScrollHandler(screen_size, fade_color=(10, 10, 10, 255))  # RGBA with max alpha
        self.entries = [(int(level_id), f"Level {int(level_id)}: {level_info.get('title', 'Unknown')}")
                        for level_id, level_info in sorted(levels_data.items(), key=lambda x: int(x[0]))]
        self.content_height = self.padding_top + len(self.entries) * self.line_height
        self.scroll.update_max_scroll(self.content_height)

        # Interaction
        self.hovered_index = -1
        self.back_button = Button("back", button_images["back"], (self.cx, screen_size[1] - 80), sound_manager)

    def handle_event(self, event, engine, mouse_pos):
        if self.back_button.is_clicked(event, mouse_pos):
            engine.menu.set_active_page(MenuState.MAIN)
            return

        self.scroll.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self.get_hovered_index(mouse_pos)
            if 0 <= index < len(self.entries):
                self.sound_manager.play_sfx("button_click")
                level_id, _ = self.entries[index]
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

        # Title outside scroll area
        self.font_manager.render(surface, "Select Level", (self.cx, 60), size=40, align_center=True, color=(255, 255, 255))

        # Scrollable content
        scroll_surf = pygame.Surface((self.screen_size[0], self.scroll.scroll_area_height), pygame.SRCALPHA)
        base_y = self.padding_top - self.scroll.scroll_offset

        for i, (_, title) in enumerate(self.entries):
            y = base_y + i * self.line_height
            if 0 <= y < self.scroll.scroll_area_height:
                is_hovered = (i == self.hovered_index)
                text = f"> {title} <" if is_hovered else title
                color = (255, 255, 100) if is_hovered else (200, 200, 200)
                self.font_manager.render(scroll_surf, text, (self.cx, y), size=28, align_center=True, color=color)

        surface.blit(scroll_surf, (0, self.scroll.scroll_area_top))
        self.scroll.render_scroll_fade(surface)

        # Hint
        self.font_manager.render(surface, "Scroll to navigate, click to play", (self.cx, self.screen_size[1] - 40),
                                 size=18, align_center=True, color=(120, 120, 120))
        self.back_button.render(surface)