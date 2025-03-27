import pygame


class FontManager:
    def __init__(self, resolution, base_resolution=(1280, 720)):
        self.resolution = resolution
        self.base_resolution = base_resolution
        self.font_path = "assets/font/font.otf"
        self.font_cache = {}

    def get_scaled_font(self, size):
        """Returns a scaled font based on screen resolution."""
        scale = min(
            self.resolution[0] / self.base_resolution[0],
            self.resolution[1] / self.base_resolution[1],
        )
        scaled_size = max(12, int(size * scale))

        if scaled_size not in self.font_cache:
            self.font_cache[scaled_size] = pygame.font.Font(self.font_path, scaled_size)

        return self.font_cache[scaled_size]

    @staticmethod
    def wrap_text(text, font, max_width):
        """Splits text into lines that fit within max_width."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def render(self, surface, text, position, size=20, color=(255, 255, 255),
               wrap=False, max_width=None, align_center=False, align_right=False,
               line_height=1.3, alpha=255):
        """Renders text directly to the given surface with optional wrapping & alignment."""
        font = self.get_scaled_font(size)
        lines = self.wrap_text(text, font, max_width) if wrap and max_width else [text]

        x, y = position
        for line in lines:
            rendered = font.render(line, True, color)
            if alpha < 255:
                rendered.set_alpha(alpha)
            rect = rendered.get_rect()

            if align_center:
                rect.centerx = x
            elif align_right:
                rect.right = x
            else:
                rect.x = x

            rect.y = y
            surface.blit(rendered, rect)
            y += int(font.get_linesize() * line_height)

    def render_to_surface(self, text, size=20, color=(255, 255, 255),
                          wrap=False, max_width=None, line_height=1.3, alpha=255):
        """Renders text to a new surface (for caching)."""
        font = self.get_scaled_font(size)
        lines = self.wrap_text(text, font, max_width) if wrap and max_width else [text]

        line_surfaces = [font.render(line, True, color) for line in lines]
        max_width_line = max((surf.get_width() for surf in line_surfaces), default=0)
        total_height = int(sum(surf.get_height() for surf in line_surfaces) * line_height)

        surface = pygame.Surface((max_width_line, total_height), pygame.SRCALPHA)
        y = 0
        for rendered in line_surfaces:
            if alpha < 255:
                rendered.set_alpha(alpha)
            surface.blit(rendered, (0, y))
            y += int(rendered.get_height() * line_height)

        return surface

    @staticmethod
    def fade_alpha(timer, fade_in, full_duration, fade_out):
        """Fades alpha in/out based on a timer and given durations."""
        total = fade_in + full_duration + fade_out
        if timer < fade_in:
            return int((timer / fade_in) * 255)
        elif timer < fade_in + full_duration:
            return 255
        elif timer < total:
            return int((1 - (timer - fade_in - full_duration) / fade_out) * 255)
        return 0
