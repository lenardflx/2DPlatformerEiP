import pygame
import os
import math

from core.game_data import get_game_data


class Background:
    def __init__(self, data):
        """Creates a background object from a dictionary of data."""
        self.image = pygame.image.load(data["image"]).convert_alpha()
        self.scale = get_game_data("background_scale")
        self.type = data.get("type", "static")
        self.speed = data.get("speed", 0)
        self.offset = 0
        self.rect = self.image.get_rect()

    def render(self, screen, camera):
        """Renders the background on the screen with proper scaling."""
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Scale image to screen size
        img_width, img_height = self.image.get_size()
        scale = min(screen_width / img_width, screen_height / img_height)
        new_size = (int(img_width * scale), int(img_height * scale))
        scaled_image = pygame.transform.scale(self.image, new_size)
        scaled_rect = scaled_image.get_rect()

        if self.type == "static":
            amount = screen_width / scaled_rect.width + 1
            for i in range(math.ceil(amount)):
                screen.blit(scaled_image, (i * scaled_rect.width, 0))

        elif self.type == "follow_camera":
            x = -camera.camera.x * self.speed
            y = -camera.camera.y * self.speed
            for i in range(-1, screen_width // scaled_rect.width + 2):
                for j in range(-1, screen_height // scaled_rect.height + 2):
                    screen.blit(
                        scaled_image,
                        (x % scaled_rect.width + i * scaled_rect.width,
                         y % scaled_rect.height + j * scaled_rect.height)
                    )

        elif self.type == "scroll":
            self.offset += self.speed
            self.offset %= scaled_rect.width
            for i in range(-1, screen_width // scaled_rect.width + 2):
                screen.blit(scaled_image, (-self.offset + i * scaled_rect.width, 0))

