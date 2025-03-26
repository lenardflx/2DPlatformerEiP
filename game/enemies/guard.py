import pygame

from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("guard")
class Guard(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level, sound_manager):
        super().__init__(x, y, sprite_path, json_path, level, sound_manager)
        self.player = player
        self.level = level
        self.speed = 40
        self.jump_force = 160
        self.damage = 1
        self.detection_range = 8  # Distance to start chasing the player
        self.kb_x = 3
        self.kb_y = 2
        self.max_health =  6
        self.health = self.max_health

        # AI flags
        self.has_jumped = True
        self.drop = False
        self.obstacle = False

        # animations
        self.state = "run"
        self.set_state("run")
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
                self.set_state("follow")
            else:
                self.patrol(level, dt)
                self.set_state("run")

        if self.on_ground:
            self.has_jumped = False

        # Jump over obstacles or gaps
        if self.drop and not self.has_jumped:
            self.jump(dt, 15 * self.speed, 120, level.gravity >= 0)
            self.has_jumped = True
        elif self.obstacle and not self.has_jumped:
            self.jump(dt, 0, 200, level.gravity >= 0)
            self.has_jumped = True

        super().update(level, dt)

        # Attack player if touching them
        if self.rect.colliderect(self.player.rect):
            self.attack()

    def patrol(self, level, dt):
        """Moves the enemy left and right, reversing direction on collisions."""
        if self.facing_right:
            self.velocity.x = self.speed * dt
        else:
            self.velocity.x = -self.speed * dt

        if not self.is_direction_safe(level, "right" if self.facing_right else "left"):
            self.velocity.x *= -1
            self.facing_right = not self.facing_right

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
