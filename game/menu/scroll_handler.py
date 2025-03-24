import pygame

class ScrollHandler:
    def __init__(self, screen_size, area_top=100, area_bottom_offset=100, scroll_speed=30, margin=40, fade_color=(0, 0, 0)):
        self.screen_size = screen_size
        self.scroll_area_top = area_top
        self.scroll_area_bottom = screen_size[1] - area_bottom_offset
        self.scroll_area_height = self.scroll_area_bottom - self.scroll_area_top

        self.scroll_offset = 0
        self.scroll_speed = scroll_speed
        self.scroll_margin = margin
        self.max_scroll = 0
        self.fade_color = fade_color

    def update_max_scroll(self, content_height):
        self.max_scroll = max(0, content_height - self.scroll_area_height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.scroll_speed

    def clamp_scroll(self):
        max_scroll = self.max_scroll + self.scroll_margin
        self.scroll_offset = max(-self.scroll_margin, min(self.scroll_offset, max_scroll))

        if self.scroll_offset < 0:
            self.scroll_offset += 4
        elif self.scroll_offset > self.max_scroll:
            self.scroll_offset -= 4

        if abs(self.scroll_offset) < 4:
            self.scroll_offset = 0
        if abs(self.scroll_offset - self.max_scroll) < 4:
            self.scroll_offset = self.max_scroll

    def render_scroll_fade(self, surface):
        fade_height = 30
        if self.scroll_offset > 0:
            top_fade = pygame.Surface((self.screen_size[0], fade_height), pygame.SRCALPHA)
            for y in range(fade_height):
                alpha = int(255 * (1 - y / fade_height))
                pygame.draw.line(top_fade, (*self.fade_color,alpha), (0, y), (self.screen_size[0], y))
            surface.blit(top_fade, (0, self.scroll_area_top))

        if self.scroll_offset < self.max_scroll:
            bottom_fade = pygame.Surface((self.screen_size[0], fade_height), pygame.SRCALPHA)
            for y in range(fade_height):
                alpha = int(255 * (1 - y / fade_height))
                pygame.draw.line(bottom_fade, (*self.fade_color,alpha), (0, fade_height - y - 1), (self.screen_size[0], fade_height - y - 1))
            surface.blit(bottom_fade, (0, self.scroll_area_bottom - fade_height))
