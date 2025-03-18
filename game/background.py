import pygame
from core.game_data import get_game_data


class Background:
    def __init__(self):
        self.image = pygame.image.load("assets/background/background.png")
        self.scale = get_game_data("background_scale")

        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_width() * self.scale,
                                             self.image.get_height() * self.scale))

    def render(self, screen, camera=None):
        screen.blit(self.image, (0, 0))
