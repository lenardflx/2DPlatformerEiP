import pygame

from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("guard")
class Guard(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level):
        super().__init__(x, y, sprite_path, json_path)
        self.player = player
        self.level = level
        self.speed = 40
        self.jump_force = 160
        self.damage = 1
        self.detection_range = 4  # Distance to start chasing the player
        self.kb_x = 3
        self.kb_y = 2
        self.max_health =  4
        self.health = self.max_health

        # AI flags
        self.has_jumped = True
        self.drop = False
        self.obstacle = False

        # animations
        self.state = "idle"
        self.sprite_index = 0
        self.image = self.sprites[self.state][self.sprite_index] if self.sprites.get(self.state) else None

    def update(self, level, dt):
        """Handles enemy movement and AI behavior."""

        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False

        # Chase player if nearby
        distance_to_player = pygame.Vector2(self.rect.midbottom).distance_to(self.player.rect.midtop)
        if not self.stun:
            if distance_to_player < self.detection_range * self.level.tile_size:
                self.chase_player(dt)
            else:
                self.patrol(level, dt)

        if self.on_ground:
            self.has_jumped = False

        # Jump over obstacles or gaps
        new_state = "jump"

        if self.drop and not self.has_jumped:
            self.jump(dt, 15 * self.speed, 120, level.gravity >= 0)
            self.has_jumped = True
        elif self.obstacle and not self.has_jumped:
            self.jump(dt, 0, 200, level.gravity >= 0)
            self.has_jumped = True
        else:
            new_state = "run"

        super().update(level, dt)
        self.state = new_state  # Update animation state

        # Attack player if touching them
        if self.rect.colliderect(self.player.rect):
            self.attack()

    def patrol(self, level, dt):
        """Moves the enemy left and right, reversing direction on collisions."""

        future_rect = self.rect.copy()

        if self.facing_right:
            self.velocity.x = self.speed * dt
            future_rect = level.get_tile_at(future_rect.left + future_rect.width + 1, future_rect.top)
        else:
            self.velocity.x = -self.speed * dt
            future_rect = level.get_tile_at(future_rect.left - 1, future_rect.top)

        if future_rect:
            self.velocity.x *= -1

    def chase_player(self, dt):
        """Moves toward the player if within detection range."""
        if self.rect.centerx < self.player.rect.centerx:
            self.velocity.x = self.speed * dt
        else:
            self.velocity.x = -self.speed * dt

    def attack(self):
        """Handles enemy attacking logic."""
        self.player.hit(self)

    def jump(self, dt, x_vel, y_vel, sgn):
        """Applies jump force to the enemy."""
        if self.facing_right:
            self.velocity.x = x_vel * dt
        else:
            self.velocity.x = -x_vel * dt
        if not sgn:
            y_vel *= -1

        self.velocity.y = -y_vel * dt
