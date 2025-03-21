import pygame
from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("drone")
class Drone(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level):
        super().__init__(x, y, sprite_path, json_path, level)
        self.player = player
        self.level = level
        self.speed = 60
        self.damage = 1
        self.detection_range = 12 * level.tile_size

        # Pathfinding smoothing
        self.direction = pygame.Vector2(0, 0)
        self.smoothing = 0.2

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
        """Make drone hover toward the player's head, adjust if blocked."""

        # 🎯 Target = Player's head (centerx, top)
        target = pygame.Vector2(self.player.rect.centerx, self.player.rect.top)
        current = pygame.Vector2(self.rect.centerx, self.rect.centery)

        direction = (target - current)

        # Detect if we're stuck (not moving for a while)
        if direction.length_squared() < 1:
            self.velocity.x = 0
            self.velocity.y = 0
            return

        # Normalize and apply smoothing
        direction = direction.normalize()
        self.direction = self.direction.lerp(direction, self.smoothing)

        # Set velocity
        base_speed = self.speed * dt
        self.velocity.x = self.direction.x * base_speed
        self.velocity.y = self.direction.y * base_speed

        # If stuck at wall, add vertical bias to move up/down around it
        probe_rect = self.rect.move(self.velocity.x * 2, self.velocity.y * 2)
        if any(probe_rect.colliderect(tile.rect) for tile in self.level.get_solid_tiles_near(self)):
            # Try to nudge up or down to escape
            self.velocity.y += (-1 if self.rect.centery > self.player.rect.centery else 1) * base_speed * 0.5

    def attack(self):
        self.player.hit(self)

    def eliminate(self):
        print("Drone eliminated")
        self.kill()
