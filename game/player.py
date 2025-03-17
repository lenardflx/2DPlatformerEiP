import pygame
from game.entities import Entity

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 12, 16)
        self.speed = 2
        self.jump_power = -5

    def handle_input(self, keys, level):
        if keys[pygame.K_LEFT]:
            self.move_horizontal(level, -self.speed)

        if keys[pygame.K_RIGHT]:
            self.move_horizontal(level, self.speed)

        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_power

    def update(self, level, dt):
        keys = pygame.key.get_pressed()
        self.handle_input(keys, level)
        super().update(level, dt)
