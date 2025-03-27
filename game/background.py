import pygame
import math
from core.game_data import get_game_data


class Background:
    def __init__(self, data):
        """Creates and scales the background once based on background_scale."""
        self.type = data.get("type", "static")
        self.speed = data.get("speed", 0)
        self.offset = 0

        # Load original image with alpha
        original_image = pygame.image.load(data["image"]).convert_alpha()

        # Get scale factor from game config
        scale = get_game_data("background_scale")
        orig_width, orig_height = original_image.get_size()
        new_size = (int(orig_width * scale), int(orig_height * scale))
        self.image = pygame.transform.scale(original_image, new_size)
        self.rect = self.image.get_rect()

    def render(self, screen, camera):
        """Renders the background horizontally."""
        iw, ih = self.rect.size
        sw, sh = screen.get_size()

        if self.type == "static":
            for i in range(-1, sw // iw + 2):
                screen.blit(self.image, (i * iw, 0))

        elif self.type == "follow_camera":
            if not camera:
                return
            cam_x = -camera.camera.x * self.speed
            base_x = int(cam_x % iw)

            for i in range(-1, sw // iw + 2):
                screen.blit(self.image, (base_x + i * iw, 0))

        elif self.type == "scroll":
            self.offset = (self.offset + self.speed) % iw
            for i in range(-1, sw // iw + 2):
                screen.blit(self.image, (-self.offset + i * iw, 0))
