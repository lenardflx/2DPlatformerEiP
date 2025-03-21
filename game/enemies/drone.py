import pygame
import math
from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("drone")
class Drone(Entity):
    def __init__(self, x, y, width, height, scale, player, level):
        super().__init__(x, y, width, height, scale)
        self.player = player
        self.level = level
        self.speed = 60  # Slightly faster
        self.damage = 1
        self.detection_range = 6 * level.tile_size

        # Pathfinding smoothing
        self.direction = pygame.Vector2(0, 0)
        self.smoothing = 0.05  # Smaller = smoother turning

        # Load animations
        self.load_sprites("assets/characters/drone.png", "assets/characters/drone.json")
        self.state = "idle"

    def update(self, level, dt):
        distance = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)

        if distance < self.detection_range and not self.stun:
            self.chase_player(dt)
            self.state = "run"
        else:
            self.state = "idle"

        # Directional flip
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False

        super().update(level, dt)

        # Check for collision with player
        if self.rect.colliderect(self.player.rect):
            self.attack()

    def chase_player(self, dt):
        """Smooth flying with hover effect."""
        target_vec = pygame.Vector2(
            self.player.rect.centerx - self.rect.centerx,
            self.player.rect.centery - self.rect.centery
        )

        if target_vec.length() != 0:
            target_vec = target_vec.normalize()

        # Smooth movement toward target
        self.direction = self.direction.lerp(target_vec, self.smoothing)

        base_speed = self.speed * dt
        self.velocity.x = self.direction.x * base_speed
        self.velocity.y = self.direction.y * base_speed

    def attack(self):
        self.player.hit(self)

    def eliminate(self):
        print("Drone eliminated")
        self.kill()
