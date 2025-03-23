import pygame
import random
from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("battery")
class Battery(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level, sound_manager):
        super().__init__(x, y, sprite_path, json_path, level,sound_manager)
        self.player = player
        self.level = level

        # Core Stats
        self.speed = 40
        self.damage = 4
        self.kb_x = 3
        self.kb_y = 6
        self.health = 1
        self.max_health = 1
        self.detection_range = 4 * level.tile_size
        self.stop_chase_range = 6 * level.tile_size
        self.explosion_radius = self.level.tile_size * 2.5

        # AI State
        self.ai_state = "idle"
        self.exploded = False
        self.playing_explode_anim = False

        # Timers
        self.idle_timer = random.randint(30, 60)
        self.patrol_timer = random.randint(60, 120)
        self.patrol_dir = random.choice([-1, 1])

    def update(self, level, dt):
        if self.stun > 0:
            self.stun -= 1
            self.velocity.x = 0
            self.set_state("idle")
            super().update(level, dt)
            return

        # Directional look
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False

        distance = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)
        close_enough = distance < self.detection_range // 2
        in_range = distance < self.detection_range
        out_of_range = distance > self.stop_chase_range

        if self.ai_state == "idle":
            self.set_state("idle")
            self.velocity.x = 0
            self.idle_timer -= 1

            if in_range:
                self.ai_state = "chase"
            elif self.idle_timer <= 0:
                self.ai_state = "patrol"
                self.patrol_timer = random.randint(60, 120)
                self.patrol_dir = random.choice([-1, 1])
                self.idle_timer = random.randint(30, 60)

        elif self.ai_state == "patrol":
            self.set_state("run")
            self.velocity.x = self.patrol_dir * self.speed * dt
            self.patrol_timer -= 1

            if self.detect_wall_ahead():
                self.patrol_dir *= -1
                self.facing_right = not self.facing_right

            if in_range:
                self.ai_state = "chase"
            elif self.patrol_timer <= 0:
                self.ai_state = "idle"

        elif self.ai_state == "chase":
            self.facing_right = self.rect.centerx < self.player.rect.centerx
            self.set_state("chase")
            direction = 1 if self.facing_right else -1
            self.velocity.x = direction * self.speed * dt

            if close_enough:
                self.ai_state = "attack"
                self.set_state("attack")
                self.velocity.x = 0
                self.sprite_index = 0
            elif out_of_range:
                self.ai_state = "idle"
                self.velocity.x = 0

        elif self.ai_state == "attack":
            self.set_state("attack")
            self.velocity.x = 0

            if self.sprite_index >= len(self.sprites["attack"]) - 1:
                self.explode()
                self.ai_state = "explode"
                self.set_state("explode")
                self.sprite_index = 0
                self.playing_explode_anim = True

        elif self.ai_state == "explode":
            self.set_state("explode")
            self.velocity.x = 0

            if self.sprite_index >= len(self.sprites["explode"]) - 1:
                self.eliminate()

        super().update(level, dt)

    def explode(self):
        """Deal AoE damage to nearby entities."""
        self.sound_manager.play_sfx("explosion")
        if self.exploded:
            return

        for entity in [self.player] + list(self.level.enemies):
            if entity == self:
                continue
            if pygame.Vector2(self.rect.center).distance_to(entity.rect.center) <= self.explosion_radius:
                if hasattr(entity, "hit"):
                    entity.hit(self)

        self.exploded = True

    def detect_wall_ahead(self):
        offset = self.rect.width if self.facing_right else -1
        probe = self.rect.move(offset, 0)
        return any(tile.rect.colliderect(probe) for tile in self.level.get_solid_tiles_near(self))

    def attack(self):
        pass  # Overridden: explosion handles damage

    def eliminate(self):
        self.kill()
