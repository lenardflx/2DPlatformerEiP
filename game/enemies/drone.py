import math
import pygame
from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("drone")
class Drone(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level, sound_manager):
        super().__init__(x, y, sprite_path, json_path, level, sound_manager)
        self.player = player
        self.level = level
        self.speed = 60
        self.damage = 1
        self.health = 6
        self.kb_x = 2
        self.kb_y = 1
        self.detection_range = 12 * level.tile_size

        self.direction = pygame.Vector2(0, 0)
        self.smoothing = 0.2
        self.rotation_angle = 0

        # Attack logic
        self.charge_cooldown = 0
        self.charge_duration = 0
        self.windup_timer = 0
        self.in_charge = False
        self.c = 0
        self.apply_gravity = False

        # Behavior tweaks
        self.overhead_offset = -40  # Hover height above player
        self.attack_range = 30      # Vertical trigger range to drop

    def update(self, level, dt):
        distance = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)

        if self.charge_cooldown > 0:
            self.charge_cooldown -= 1

        # Attack check
        if self.rect.colliderect(self.player.rect):
            self.sound_manager.play_sfx("drone_attack") # von Philipp: könnte falsch sein
            self.attack()

        if self.in_charge:
            self.charge_duration -= 1
            if self.charge_duration <= 0:
                self.in_charge = False
                self.velocity = pygame.Vector2(0, 0)
            else:
                self.velocity.y += 0.25 * self.speed * dt
        elif distance < self.detection_range and not self.stun:
            self.smart_chase(dt)
            self.set_state("run")
        else:
            self.velocity *= 0.9  # slow down
            self.set_state("idle")

        # Rotation toward player (limited to slight tilts)
        dx = self.player.rect.centerx - self.rect.centerx
        max_angle = 20
        self.rotation_angle = max(-max_angle, min(max_angle, dx * 0.1))

        # Directional flip (for animation)
        self.facing_right = dx >= 0

        super().update(level, dt)

    def flip_gravity(self):
        pass

    def smart_chase(self, dt):

        directions = [(-1, 0, 0), (-1, -1, 1), (0, -1, 0), (1, -1, 1), (1, 0, 0), (1, 1, 1), (0, 1, 0), (-1, 1, 1)]
        best_value = float('inf')
        best_target = None

        corner = self.rect.topleft
        tmp = 0
        corners = [(self.rect.topleft), (self.rect.topright), (self.rect.bottomleft), (self.rect.bottomright)]
        
        for c in corners:
            x = c[0] // self.level.tile_size
            y = c[1] // self.level.tile_size

            if self.level.mp[x][y] > tmp and self.level.mp[x][y] != 1000:
                tmp = self.level.mp[x][y]
                corner = [x, y]

        for index, dir in enumerate(directions):
            dx = dir[0]
            dy = dir[1]
            cnr = dir[2]
            
            gx = corner[0] + dx
            gy = corner[1] + dy

            if 0 <= gx < self.level.grid_width and 0 <= gy < self.level.grid_height:
                if cnr == 1:    #Falls diagonal
                    if (self.level.mp[corner[0] + directions[(index-1)%8][0]][corner[1] + directions[(index-1)%8][1]] == 1000
                    or
                    self.level.mp[corner[0] + directions[(index+1)%8][0]][corner[1] + directions[(index+1)%8][1]] == 1000):
                        continue
                    
                val = self.level.mp[gx][gy]
                if val < best_value:
                    best_value = val
                    best_target = (gx, gy)

        if best_target:
            # Center of the target tile
            tx = best_target[0]
            ty = best_target[1]
            target_x = tx * self.level.tile_size + self.level.tile_size // 2
            target_y = ty * self.level.tile_size + self.level.tile_size // 2

            direction = pygame.Vector2(target_x - self.rect.centerx, target_y - self.rect.centery)

            if direction.length() > 1:
                direction = direction.normalize()
                self.velocity = direction * self.speed * dt
        else:
            self.velocity *= 0.5  # gently stop if no path

    def attack(self):
        self.player.hit(self)

    def eliminate(self):
        super().eliminate()

    def render(self, screen, camera):
        """Render the drone with visual rotation, but keep hitbox unchanged."""
        render_pos = camera.apply(self)
        image = self.image

        # Rotate only the image
        rotated_image = pygame.transform.rotate(image, self.rotation_angle)
        rotated_rect = rotated_image.get_rect(center=(render_pos[0] + self.render_offset[0] + image.get_width() // 2,
                                                      render_pos[1] + self.render_offset[1] + image.get_height() // 2))

        # Draw rotated image
        screen.blit(rotated_image, rotated_rect.topleft)
        self.render_health_bar(screen, camera)

        # Optional: Draw hitbox (collision box)
        # pygame.draw.rect(screen, (255, 0, 0), camera.apply(self), 1)
