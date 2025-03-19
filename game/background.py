import os
import pygame
import math
from core.game_data import get_game_data

class Background:
    def __init__(self, data):
        """Initializes a background layer with parallax effect."""
        self.image = pygame.image.load(os.path.join("assets/background/", data["file"])).convert_alpha()
        self.scale = get_game_data("background_scale")
        self.speed = data["speed"]
        self.follow_camera = data["follow_camera"]

        # Store original image for scaling later
        self.original_image = self.image
        self.rect = self.image.get_rect()

    def render(self, screen, camera):
        """Renders the background with correct scaling and parallax effect."""
        # Scale image dynamically to match screen size
        screen_width, screen_height = screen.get_size()
        scaled_width = int(self.original_image.get_width() * self.scale)
        scaled_height = int(self.original_image.get_height() * self.scale)

        if self.image.get_width() != scaled_width or self.image.get_height() != scaled_height:
            self.image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height))
            self.rect = self.image.get_rect()

        # Compute how many times the background needs to be drawn
        clone_amount = math.ceil(screen_width / self.rect.width) + 1  # Ensure full coverage

        # Compute camera offsets once
        x_offset = -camera.camera.x * self.speed if self.follow_camera else 0
        y_offset = -camera.camera.y * self.speed if self.follow_camera else 0

        # Render repeated backgrounds
        for i in range(clone_amount):
            screen.blit(self.image, (self.rect.width * i + x_offset, y_offset))
