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
        collision = check_collision(self, level, dx=speed)
        if collision == "border left":
            self.x = 0
        elif collision == "border right":
            self.x = level.scale * (len(level.tiles) - 1) - self.width
        elif collision != "solid":
            self.x += speed

    def move_vertical(self, level, dt):
        if not self.on_ground:
            self.velocity_y = self.velocity_y + level.gravity * dt

        collision = check_collision(self, level, dx=dt)
        if collision == "solid":
            self.velocity_y = 0
            self.on_ground = True
        elif collision == "border top":
            self.velocity_y = 0
            self.on_ground = False
            self.y = 0
        elif collision == "border bottom":
            self.velocity_y = 0
            self.on_ground = True
            self.y = level.height - self.height
        else:
            self.on_ground = False


        if check_collision(self, level, dy=-self.height) == "solid" and self.velocity_y < 0:
            self.velocity_y = 0

        #self.y += self.velocity_y

    def update(self, level, dt):
        self.move_vertical(level, dt)

    def render(self, screen, color=(255, 255, 255)):
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
