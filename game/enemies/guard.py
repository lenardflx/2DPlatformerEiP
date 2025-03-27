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
        self.damage = 1
        self.detection_range = 8  # Distance to start chasing the player
        self.kb_x = 3
        self.kb_y = 2
        self.max_health = 6
        self.health = self.max_health

        # animations
        self.state = "run"
        self.set_state("run")
        self.sprite_index = 0
        self.image = self.sprites[self.state][self.sprite_index] if self.sprites.get(self.state) else None

    def update(self, level, dt):
        """Handles enemy movement and AI behavior."""
        if not self.is_dying:
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

            # Attack player if touching them
            if self.rect.colliderect(self.player.rect):
                self.attack()

        super().update(level, dt)

    def patrol(self, level, dt):
        """Moves the enemy left and right, reversing direction on collisions or drops."""
        dir_str = "right" if self.facing_right else "left"
        safe = self.is_direction_safe(level, dir_str)

        if safe:
            # Nur setzen, wenn der Guard sich wirklich bewegen darf
            self.velocity.x = self.speed * dt if self.facing_right else -self.speed * dt
        else:
            # Bleib stehen, damit er nicht "zittert", und dreh erst nach kurzer Pause um
            self.velocity.x = 0
            self.facing_right = not self.facing_right

    def chase_player(self, dt):
        """Moves toward the player if within detection range."""
        if self.rect.centerx < self.player.rect.centerx:
            self.velocity.x = self.speed * dt
        else:
            self.velocity.x = -self.speed * dt

    def attack(self):
        """Handles enemy attacking logic."""
        if self.player.immunity_frames:
            return
        self.sound_manager.play_sfx("guard_attack")
        self.player.hit(self)
