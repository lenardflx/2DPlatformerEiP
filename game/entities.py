import pygame
from game.collision import check_collision

class Entity:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False

    def move_horizontal(self, level, speed):
        if speed > 0 and check_collision(self, level, dx=speed) != "solid":
            self.x += speed
        elif speed < 0 and check_collision(self, level, dx=speed) != "solid":
            self.x += speed

    def move_vertical(self, level, dt):
        if not self.on_ground:
            self.velocity_y += level.gravity * dt

        collision = check_collision(self, level, dy=self.velocity_y)

        if collision == "solid":
            if self.velocity_y > 0:
                self.velocity_y = 0
                self.on_ground = True
            elif self.velocity_y < 0:
                self.velocity_y = 0
        elif collision == "death":
            print("tot")
            self.x, self.y = 50, 50
            self.velocity_y = 0
            self.on_ground = False
        else:
            self.on_ground = False

        self.y += self.velocity_y

    def update(self, level, dt):
        self.move_vertical(level, dt)

    def render(self, screen, color=(255, 255, 255)):
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
