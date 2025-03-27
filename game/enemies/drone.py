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
        tile_size = self.level.tile_size
        grid_x = self.rect.centerx // tile_size
        grid_y = self.rect.centery // tile_size
        current_pos = pygame.Vector2(self.rect.center)

        # Initialize movement tracking
        if not hasattr(self, "target_tile"):
            self.target_tile = (grid_x, grid_y)
            self.target_pos = pygame.Vector2(
                self.target_tile[0] * tile_size + tile_size // 2,
                self.target_tile[1] * tile_size + tile_size // 2
            )
            self.stuck_counter = 0
            self.prev_pos = current_pos

        # Step 1: move toward target tile center
        to_target = self.target_pos - current_pos
        if to_target.length_squared() > 4:  # allow ~2px tolerance
            self.velocity = to_target.normalize() * self.speed * dt
            return

        # Snap into place
        self.rect.center = (int(self.target_pos.x), int(self.target_pos.y))
        self.velocity = pygame.Vector2(0, 0)

        # Step 2: select next tile from current location
        grid_x = self.rect.centerx // tile_size
        grid_y = self.rect.centery // tile_size
        current_val = self.level.mp[grid_x][grid_y]

        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        best_tile = None
        best_value = float("inf")

        for dx, dy in directions:
            nx, ny = grid_x + dx, grid_y + dy
            if not (0 <= nx < self.level.grid_width and 0 <= ny < self.level.grid_height):
                continue
            val = self.level.mp[nx][ny]
            if val >= best_value or val != current_val - 1:
                continue

            # Prevent diagonal corner clipping
            if dx != 0 and dy != 0:
                if (self.level.tile_grid[grid_y][ny] or self.level.tile_grid[ny][grid_x]):
                    continue

            best_tile = (nx, ny)
            best_value = val

        # Step 3: set new target tile
        if best_tile:
            self.target_tile = best_tile
            self.target_pos = pygame.Vector2(
                best_tile[0] * tile_size + tile_size // 2,
                best_tile[1] * tile_size + tile_size // 2
            )

        # Step 4: stuck logic
        if current_pos.distance_to(self.prev_pos) < 0.5:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.prev_pos = current_pos

        if self.stuck_counter > 30:
            nudge = pygame.Vector2(1 if self.facing_right else -1, 0)
            self.velocity += nudge * 0.2 * self.speed * dt

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
        pygame.draw.rect(screen, (255, 0, 0), camera.apply(self), 1)
