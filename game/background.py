import os.path

import pygame
from core.game_data import get_game_data


class Background:
    def __init__(self, data):
        self.image = pygame.image.load(os.path.join("assets/background/", data["file"])).convert_alpha()
        self.scale = get_game_data("background_scale")
        self.speed = data["speed"]
        self.follow_camera = data["follow_camera"]

        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_width() * self.scale,
                                             self.image.get_height() * self.scale))
        self.rect = self.image.get_rect()

    def render(self, screen, camera):
        clone_amount = camera.width // self.rect.width * 2
        for i in range(clone_amount):
            if self.follow_camera:
                off = (self.rect.width * i - camera.camera.x * self.speed, -camera.camera.y * self.speed)
            else:
                off = (self.rect.width * i, 0)
            screen.blit(self.image, off)
