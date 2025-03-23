from game.menu.menu_structure import MenuPage, Button
from game.menu.scroll_handler import ScrollHandler
import pygame

class SettingsMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, controls, sound_manager):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.controls = controls
        self.sound_manager = sound_manager
        self.waiting_for_key = None

        # Sliders
        self.music_volume = sound_manager.music_volume
        self.sfx_volume = sound_manager.sfx_volume
        self.slider_w = 180
        self.slider_h = 14
        self.slider_gap = 220
        self.slider_y = 60  # relative to scroll start

        # Scroll
        self.scroll = ScrollHandler(screen_size)
        self.line_height = 42
        total_content_height = self.slider_y + 60 + len(controls.controls) * self.line_height + 120
        self.scroll.update_max_scroll(total_content_height)

        # States
        self.drag_music = False
        self.drag_sfx = False

        # Back button
        self.back_button = Button("back", button_images["back"], (screen_size[0] // 2, screen_size[1] - 60), sound_manager)

    def handle_event(self, event, engine, mouse_pos):
        self.scroll.handle_event(event)
        relative_mouse = (mouse_pos[0], mouse_pos[1] - self.scroll.scroll_area_top)

        if self.back_button.is_clicked(event, mouse_pos):
            engine.menu.set_active_page(engine.menu.back_redirect)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Shift mouse position into scroll content space

            if self.get_music_slider_rect().collidepoint(relative_mouse):
                self.drag_music = True
                self.set_music_volume(relative_mouse[0])
            elif self.get_sfx_slider_rect().collidepoint(relative_mouse):
                self.drag_sfx = True
                self.set_sfx_volume(relative_mouse[0])

            else:
                for i, action in enumerate(self.controls.controls):
                    for j, rect in enumerate(self.get_key_rects(i)):
                        adjusted_rect = rect.move(0, self.scroll.scroll_area_top)  # align scroll area
                        if adjusted_rect.collidepoint(mouse_pos):
                            self.waiting_for_key = (action, j)
                            return

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drag_music = self.drag_sfx = False

        elif event.type == pygame.MOUSEMOTION:
            if self.drag_music:
                self.set_music_volume(relative_mouse[0])
            elif self.drag_sfx:
                self.set_sfx_volume(relative_mouse[0])

        elif event.type == pygame.KEYDOWN and self.waiting_for_key:
            action, index = self.waiting_for_key
            self.controls.bind_key(action, event.key)
            self.waiting_for_key = None

    def update(self, mouse_pos):
        self.scroll.clamp_scroll()
        self.back_button.update(mouse_pos)

    def set_music_volume(self, mouse_x):
        rect = self.get_music_slider_rect()
        self.music_volume = max(0, min(1, (mouse_x - rect.x) / self.slider_w))
        self.sound_manager.set_music_volume(self.music_volume)

    def set_sfx_volume(self, mouse_x):
        rect = self.get_sfx_slider_rect()
        self.sfx_volume = max(0, min(1, (mouse_x - rect.x) / self.slider_w))
        self.sound_manager.set_sfx_volume(self.sfx_volume)

    def get_music_slider_rect(self):
        cx = self.screen_size[0] // 2 - self.slider_gap // 2
        return pygame.Rect(cx - self.slider_w // 2, self.slider_y - self.scroll.scroll_offset, self.slider_w, self.slider_h)

    def get_sfx_slider_rect(self):
        cx = self.screen_size[0] // 2 + self.slider_gap // 2
        return pygame.Rect(cx - self.slider_w // 2, self.slider_y - self.scroll.scroll_offset, self.slider_w, self.slider_h)

    def get_key_rects(self, i):
        base_y = self.slider_y + 80 + i * self.line_height - self.scroll.scroll_offset
        x1 = self.screen_size[0] // 2 + 60
        return [pygame.Rect(x1, base_y, 90, 30), pygame.Rect(x1 + 100, base_y, 90, 30)]

    def render_slider(self, surf, label, rect, value, color):
        pygame.draw.rect(surf, (40, 40, 40), rect.inflate(8, 8), border_radius=4)
        pygame.draw.rect(surf, (0, 200, 200), rect.inflate(4, 4), 2, border_radius=3)
        pygame.draw.rect(surf, (100, 100, 100), rect, border_radius=3)
        fill = pygame.Rect(rect.x, rect.y, int(rect.width * value), rect.height)
        pygame.draw.rect(surf, color, fill, border_radius=3)
        self.font_manager.render(surf, label, (rect.centerx, rect.top - 25 - self.scroll.scroll_area_top), size=20, align_center=True)

    def render(self, surface):
        self.font_manager.render(surface, "Settings", (self.screen_size[0] // 2, 40), size=42, align_center=True)

        # Scrolling content
        scroll_surf = pygame.Surface((self.screen_size[0], self.scroll.scroll_area_height), pygame.SRCALPHA)

        # Sliders
        self.render_slider(scroll_surf, "Music", self.get_music_slider_rect(), self.music_volume, (0, 255, 200))
        self.render_slider(scroll_surf, "SFX", self.get_sfx_slider_rect(), self.sfx_volume, (255, 200, 0))

        # Controls section
        self.font_manager.render(
            scroll_surf,
            "Controls",
            (100, self.slider_y + 40 - self.scroll.scroll_offset - self.scroll.scroll_area_top),
            size=28
        )

        for i, (action, keys) in enumerate(self.controls.controls.items()):
            y = self.slider_y + 80 + i * self.line_height - self.scroll.scroll_offset - self.scroll.scroll_area_top
            self.font_manager.render(scroll_surf, action.replace("_", " ").title(), (100, y + 8), size=20)

            for j, rect in enumerate(self.get_key_rects(i)):
                color = (255, 80, 80) if self.waiting_for_key == (action, j) else (50, 50, 50)
                pygame.draw.rect(scroll_surf, (0, 200, 255), rect.inflate(6, 6), 2, border_radius=4)
                pygame.draw.rect(scroll_surf, color, rect, border_radius=3)
                key = pygame.key.name(keys[j]) if keys[j] is not None else "UNBOUND"
                self.font_manager.render(scroll_surf, key, rect.center, size=18, align_center=True)

        surface.blit(scroll_surf, (0, self.scroll.scroll_area_top))
        self.back_button.render(surface)
        self.scroll.render_scroll_fade(surface)
