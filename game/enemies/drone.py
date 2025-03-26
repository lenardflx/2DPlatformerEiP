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

    def smart_chase(self, dt):
        """
        Move deeply into the next grid cell with the smallest number.
        """
        # Current grid position
        current_grid_x = int(self.rect.centerx / 32)
        current_grid_y = int(self.rect.centery / 32)

        # Check adjacent cells (including diagonals)
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]

        # Track the best (smallest) number and its location
        best_value = float('inf')
        best_target = None

        for dx, dy in directions:
            new_x, new_y = current_grid_x + dx, current_grid_y + dy

            # Bounds and validity check
            try:
                cell_value = self.level.mp[new_x][new_y]

                # Find the smallest valid number
                if cell_value is not None and cell_value < best_value:
                    best_value = cell_value
                    best_target = (new_x, new_y)
            except (IndexError, TypeError):
                continue

        # Move towards the best target
        if best_target:
            target_grid_x, target_grid_y = best_target

            # Target deep into the next grid cell
            target_x = target_grid_x * 32 + 16 + (32 * 0.75 * (
                1 if target_grid_x > current_grid_x else -1 if target_grid_x < current_grid_x else 0))
            target_y = target_grid_y * 32 + 16 + (32 * 0.75 * (
                1 if target_grid_y > current_grid_y else -1 if target_grid_y < current_grid_y else 0))

            # Calculate direction vector
            drone_pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
            target_pos = pygame.Vector2(target_x, target_y)

            direction = (target_pos - drone_pos).normalize()

            # Moderate speed movement
            self.velocity = direction * self.speed * dt

            # Force deep penetration into the next grid cell
            if (abs(self.rect.centerx - target_x) < 10 and
                    abs(self.rect.centery - target_y) < 10):
                self.rect.centerx = target_x
                self.rect.centery = target_y
        else:
            # No valid movement found
            self.state = "idle"
            self.velocity = pygame.Vector2(0, 0)


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

        # Optional: Draw hitbox (collision box)
        pygame.draw.rect(screen, (255, 0, 0), camera.apply(self), 1)
