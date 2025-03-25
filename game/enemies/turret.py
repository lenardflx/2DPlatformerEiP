import pygame
import math
from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("turret")
class Turret(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level, sound_manager):
        super().__init__(x, y, sprite_path, json_path, level, sound_manager)
        self.player = player
        self.level = level

        self.state = "idle"
        self.damage = 1
        self.attack_range = 6 * level.tile_size
        self.cooldown = 90
        self.current_cooldown = 0
        self.facing_right = True
        self.y_gun_offset = 4
        self.beam_duration = 10
        self.beam_timer = 0
        self.beam_start = None
        self.beam_end = None

    def flip_gravity(self):
        pass  # Turret ignores gravity flipping

    def update(self, level, dt):
        if self.health <= 0:
            self.eliminate()
            return

        distance = abs(self.rect.centerx - self.player.rect.centerx)
        in_range = distance <= self.attack_range and self.line_of_sight()

        if in_range:
            self.facing_right = self.rect.centerx < self.player.rect.centerx

        if in_range:
            if self.current_cooldown == 0:
                self.set_state("attack")
                if self.sprite_index >= len(self.sprites["attack"]) - 1:
                    self.shoot()
                    #self.set_state("shoot")
                    self.sprite_index = 0
                    self.beam_timer = self.beam_duration
                    self.current_cooldown = self.cooldown
            else:
                self.current_cooldown -= 1
        else:
            self.set_state("idle")
            self.current_cooldown = max(0, self.current_cooldown - 1)

        if self.beam_timer > 0:
            self.beam_timer -= 1

        # No gravity or velocity
        self.velocity = pygame.Vector2(0, 0)
        self.update_animation(dt)

    def shoot(self):
        self.beam_start = (self.rect.centerx, self.rect.top + self.y_gun_offset)
        self.beam_end = self.find_wall_in_direction()
        if self.player.rect.clipline(self.beam_start, self.beam_end):
            self.player.hit(self)

    def line_of_sight(self):
        x0, y = self.rect.centerx, self.rect.top + self.y_gun_offset
        x1 = self.player.rect.centerx
        step = 1 if x1 > x0 else -1
        for x in range(x0, x1, step * self.level.tile_size):
            tile = self.level.get_tile_at(x, y)
            if tile and tile.solid:
                return False
        return True

    def find_wall_in_direction(self):
        x = self.rect.centerx
        y = self.rect.top + self.y_gun_offset
        step = self.level.tile_size if self.facing_right else -self.level.tile_size
        max_dist = 10 * self.level.tile_size
        for i in range(0, max_dist, abs(step)):
            check_x = x + i if self.facing_right else x - i
            tile = self.level.get_tile_at(check_x, y)
            if tile and tile.solid:
                return (check_x, y)
        return (x + step * 10, y)

    def render(self, screen, camera):
        # Calculate angle only if in range
        player_center = self.player.rect.center
        turret_center = self.rect.center
        dx = player_center[0] - turret_center[0]
        dy = player_center[1] - turret_center[1]
        angle = math.degrees(math.atan2(dy, dx))

        # Grab current sprite frame
        frame = self.sprites[self.state][self.sprite_index]

        # Apply rotation (don’t flip vertically ever)
        rotated_sprite = pygame.transform.rotate(frame, -angle)

        # Recalculate draw position
        rotated_rect = rotated_sprite.get_rect(center=turret_center)
        screen.blit(rotated_sprite, camera.apply(rotated_rect))

        # Beam (pretty)
        if self.beam_timer > 0 and self.beam_start and self.beam_end:
            start = camera.apply(pygame.Rect(self.beam_start, (0, 0))).topleft
            end = camera.apply(pygame.Rect(self.beam_end, (0, 0))).topleft
            pygame.draw.line(screen, (40, 100, 255), start, end, 3)
            pygame.draw.line(screen, (170, 210, 255), start, end, 1)

        self.render_health_bar(screen, camera)
