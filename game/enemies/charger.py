import pygame
import random

from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("charger")
class Charger(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level, sound_manager):
        super().__init__(x, y, sprite_path, json_path, level, sound_manager)
        self.player = player
        self.level = level

        # Core stats
        self.base_speed = 32
        self.charge_speed = 1000
        self.damage = 3
        self.kb_x = 5
        self.kb_y = 8
        self.max_health = 16
        self.health = self.max_health
        self.detection_range = 7 * self.level.tile_size

        # AI state
        self.ai_state = "idle"
        self.commit_to_charge = False

        # Timers
        self.attack_windup_timer = 0
        self.charge_timer = 0
        self.charge_cooldown = 0
        self.idle_timer = random.randint(30, 60)
        self.patrol_timer = random.randint(60, 120)

        # Patrol
        self.patrol_dir = random.choice([-1, 1])
        self.patrol_speed_variation = random.uniform(0.8, 1.2)

    def update(self, level, dt):
        
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False

        if self.charge_cooldown > 0:
            self.charge_cooldown -= 1

        # Player detection
        distance = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)
        player_visible = distance < self.detection_range and self.has_line_of_sight()

        # AI state
        match self.ai_state:
            case "idle":
                if self.on_ground:
                    self.velocity.x = 0
                if self.stun == 0:
                    if player_visible:
                        if self.charge_cooldown > 0:
                            self.set_state("await")
                            self.ai_state = "await"
                        else:
                            self.ai_state = "attack"
                            self.attack_windup_timer = 30
                            self.face_player()
                    else:
                        self.ai_state = "patrol"
                        self.patrol_timer = random.randint(60, 120)
                        self.patrol_dir = 1 if self.facing_right else -1
                        if not self.is_direction_safe(level, "right" if self.facing_right else "left"):
                            self.patrol_dir *= -1
                            self.facing_right = not self.facing_right
                        self.patrol_speed_variation = random.uniform(0.8, 1.2)
                        self.idle_timer = random.randint(30, 60)

            case "patrol":
                self.set_state("run")
                self.patrol_timer -= 1
                speed = self.base_speed * self.patrol_speed_variation * dt
                self.velocity.x = self.patrol_dir * speed
                self.facing_right = self.patrol_dir > 0

                if self.hit_edge:
                    self.patrol_dir *= -1
                    self.facing_right = not self.facing_right
                    self.hit_edge = False

                if player_visible and self.charge_cooldown <= 0:
                    self.ai_state = "attack"
                    self.attack_windup_timer = 30
                    self.face_player()
                    self.commit_to_charge = True
                elif self.patrol_timer <= 0:
                    self.ai_state = "idle"

            case "attack":
                self.set_state("attack")
                self.velocity.x = 0
                self.face_player()
                self.commit_to_charge = True

                # Only attack after windup
                frames = self.sprites.get("attack", [])
                if self.sprite_index >= len(frames) - 1:
                    self.ai_state = "charge"
                    self.charge_timer = 120
                    self.sprite_index = 0

            case "charge":
                self.set_state("charge")
                self.charge_timer -= 1

                accel = 0.25 * self.charge_speed * dt
                if self.facing_right:
                    self.velocity.x = min(self.velocity.x + accel, self.charge_speed * dt)
                else:
                    self.velocity.x = max(self.velocity.x - accel, -self.charge_speed * dt)

                # Attack on frontal collision
                if self.rect.colliderect(self.player.rect):
                    aligned = (self.facing_right and self.player.rect.centerx > self.rect.centerx) or \
                              (not self.facing_right and self.player.rect.centerx < self.rect.centerx)
                    if aligned:
                        self.attack()

                if self.charge_timer <= 0:
                    self.velocity.x = 0
                    self.charge_cooldown = 90
                    self.ai_state = "await"
                    self.set_state("await")
                    self.commit_to_charge = False

                if self.hit_edge:
                    self.velocity.x = 0
                    self.hit_edge = False
                    self.charge_cooldown = 90
                    self.charge_timer = 0
                    self.ai_state = "idle"
                    self.set_state("idle")
                    self.commit_to_charge = False
                    self.stun = 90
                    if self.facing_right:
                        self.knockback(-3, -1)
                    else:
                        self.knockback(3, -1)

            case "await":
                self.velocity.x = 0
                self.set_state("await")
                self.face_player()

                if self.commit_to_charge:
                    self.ai_state = "attack"
                    self.attack_windup_timer = 30
                    self.face_player()
                elif player_visible and self.charge_cooldown <= 0:
                    self.ai_state = "attack"
                    self.attack_windup_timer = 30
                    self.face_player()
                    self.commit_to_charge = True
                elif not player_visible:
                    self.ai_state = "idle"

        super().update(level, dt)

    def has_line_of_sight(self):
        """Checks for solid tiles between self and player."""
        start = pygame.Vector2(self.rect.center)
        end = pygame.Vector2(self.player.rect.center)
        direction = (end - start)
        steps = int(direction.length() // self.level.tile_size)
        if steps == 0:
            return True
        direction = direction.normalize() * self.level.tile_size
        pos = start
        for _ in range(steps):
            pos += direction
            tile = self.level.get_tile_at(pos.x, pos.y)
            if tile and getattr(tile, "solid", False):
                return False
        return True

    #def detect_wall_ahead(self):
    #    offset = self.rect.width if self.facing_right else -1
    #    probe = self.rect.move(offset, 0)
    #    return any(tile.rect.colliderect(probe) for tile in self.level.get_solid_tiles_near(self))

    def face_player(self):
        self.facing_right = self.rect.centerx < self.player.rect.centerx

    def attack(self):
        if self.stun == 0:
            self.player.hit(self)

    def hit(self, attacker, stun = 0):
        if self.stun != 0:
            super().hit(attacker, 0)