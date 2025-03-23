import pygame


class FontManager:
    def __init__(self, resolution, base_resolution=(1280, 720),):
        self.resolution = resolution
        self.base_resolution = base_resolution
        self.font_path = "assets/font/font.otf"
        self.font_cache = {}

    def get_scaled_font(self, size):
        """Returns a scaled font based on screen resolution."""
        scale = min(self.resolution[0] / self.base_resolution[0], self.resolution[1] / self.base_resolution[1])
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
            test_line = f"{current_line}{word} "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = f"{word} "

        if current_line:
            lines.append(current_line.strip())

        return lines

    def render(self, surface, text, position, size=20, color=(255, 255, 255),
               wrap=False, max_width=None, align_center=False, align_right=False,
               line_height=1.3, alpha=255):
        """Renders text with optional alignment and wrapping."""
        font = self.get_scaled_font(size)

        if wrap and max_width:
            lines = self.wrap_text(text, font, max_width)
        else:
            lines = [text]

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

    @staticmethod
    def fade_alpha(timer, fade_in, full_duration, fade_out):
        total = fade_in + full_duration + fade_out
        if timer < fade_in:
            return int((timer / fade_in) * 255)
        elif timer < fade_in + full_duration:
            return 255
        elif timer < total:
            return int((1 - (timer - fade_in - full_duration) / fade_out) * 255)
        return 0
