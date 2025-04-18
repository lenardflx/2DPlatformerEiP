import math
import pygame
from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("emp_radar")
class EMP_Radar(Entity):
    def __init__(self, x, y, level, player):
        super().__init__(x, y, "assets/characters/EMP.png", "assets/characters/EMP.json", level, None)
        self.max_health = 1
        self.health = self.max_health
        self.level = level
        self.apply_gravity = False
        self.lifetime = 5.0
        self.range = 200
        self.player = player

    def update(self, level, dt):
        super().update(level, dt)
        if self.lifetime > 0:
            self.lifetime -= dt
        else:
            self.eliminate()
        self.disable()

    def eliminate(self):
        self.level.player.abilities_blocked = False
        super().eliminate()

    def disable(self):
        distance = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)
        if distance <= self.range:
            self.player.abilities_blocked = True
        else:
            self.player.abilities_blocked = False