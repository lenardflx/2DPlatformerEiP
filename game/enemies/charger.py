import pygame

from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("charger")
class Charger(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level):
        super().__init__(x, y, sprite_path, json_path, level)
        self.player = player
        self.level = level
        self.speed = 32
        self.max_speed = 1200
        self.jump_force = 100
        self.damage = 3
        self.detection_range = 7  # Distance to start chasing the player
        self.is_chasing = False
        self.chase_timer = 0
        self.kb_x = 6
        self.kb_y = 4
        self.max_health = 16
        self.health = self.max_health
        self.max_stun = 120

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

        if self.stun > 0:
            self.max_stun -= 1

        if self.max_stun == 0 or self.stun == 0:
            self.max_stun = 120
            self.stun = 0

        # Chase player if nearby
        distance_to_player = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)
        if not self.stun:
            if distance_to_player < self.detection_range * self.level.tile_size:
                if self.chase_timer == 0:
                    if self.rect.centerx < self.player.rect.centerx:
                        self.facing_right = True
                    else:
                        self.facing_right = False
                self.is_chasing = True

        if self.hit_edge:
            self.hit_edge = not self.hit_edge
            self.velocity.x = 0
            self.is_chasing = False
            self.stun = 120

        if self.is_chasing:
            self.chase_timer += 1
            self.chase_player(dt)
        else:
            self.chase_timer = 0
            if self.stun == 0:
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
        if self.chase_timer < 90:
            self.velocity.x = 0
        else:
            if self.facing_right:
                self.velocity.x += 0.33 * (self.speed * dt)
            else:
                self.velocity.x -= 0.33 * (self.speed * dt)

            if self.velocity.x > self.max_speed * dt:
                self.velocity.x = self.max_speed * dt
            elif self.velocity.x < -self.max_speed * dt:
                self.velocity.x = -self.max_speed * dt
        
    def attack(self):
        """Handles enemy attacking logic."""
        if self.stun == 0:
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

    def hit(self, attacker):
        if self.stun != 0:
            super().hit(attacker)
