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
        self.rotation_angle = 0

        # Movement tracking
        self.target_tile = None
        self.target_pos = self.rect.center

        # Attack logic
        self.charge_cooldown = 0
        self.charge_duration = 0
        self.windup_timer = 0
        self.in_charge = False
        self.apply_gravity = False

        # Behavior tweaks
        self.overhead_offset = -40
        self.attack_range = 30

    def update(self, level, dt):
        distance = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)

        if self.charge_cooldown > 0:
            self.charge_cooldown -= 1

        if self.rect.colliderect(self.player.rect):
            self.sound_manager.play_sfx("drone_attack")
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
            self.velocity *= 0.9
            self.set_state("idle")

        # Rotation toward player
        dx = self.player.rect.centerx - self.rect.centerx
        max_angle = 20
        self.rotation_angle = max(-max_angle, min(max_angle, dx * 0.1))
        self.facing_right = dx >= 0

        super().update(level, dt)

    def smart_chase(self, dt):
        """Chase the player, but avoid obstacles"""
        tile_size = self.level.tile_size
        center_x, center_y = self.rect.center

        # Move toward current target if one exists
        if self.target_tile:
            tx, ty = self.target_tile
            target_px = tx * tile_size + tile_size // 2
            target_py = ty * tile_size + tile_size // 2
            dx = target_px - center_x
            dy = target_py - center_y

            if dx * dx + dy * dy > 4:
                length = math.hypot(dx, dy)
                self.velocity = pygame.Vector2(dx / length * self.speed * dt, dy / length * self.speed * dt)
                return
            else:
                self.rect.center = (target_px, target_py)
                self.velocity = pygame.Vector2(0, 0)

        # Select next tile
        grid_x = center_x // tile_size
        grid_y = center_y // tile_size
        current_val = self.level.mp[int(grid_x)][int(grid_y)]

        # Step 1: Collect cardinal candidates
        cardinal_dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        best_val = 999
        best_cardinal = None
        second_best_cardinal = None

        for dx, dy in cardinal_dirs:
            nx, ny = int(grid_x + dx), int(grid_y + dy)
            if 0 <= nx < self.level.grid_width and 0 <= ny < self.level.grid_height:
                val = self.level.mp[nx][ny]
                if val < 999:
                    if val < best_val:
                        second_best_cardinal = best_cardinal
                        best_val = val
                        best_cardinal = ((dx, dy), val, (nx, ny))
                    elif val == best_val and not second_best_cardinal:
                        second_best_cardinal = ((dx, dy), val, (nx, ny))

        if not best_cardinal:
            self.target_tile = None
            return

        # Step 2: Check diagonal shortcut from two best cardinals
        if second_best_cardinal:
            (dx1, dy1), _, _ = best_cardinal
            (dx2, dy2), _, _ = second_best_cardinal

            diag_dx = dx1 + dx2
            diag_dy = dy1 + dy2

            if abs(diag_dx) == 1 and abs(diag_dy) == 1:
                diag_x = int(grid_x + diag_dx)
                diag_y = int(grid_y + diag_dy)

                if (0 <= diag_x < self.level.grid_width and
                    0 <= diag_y < self.level.grid_height and
                    not self._is_solid(int(grid_x + diag_dx), int(grid_y)) and
                    not self._is_solid(int(grid_x), int(grid_y + diag_dy))):

                    diag_val = self.level.mp[diag_x][diag_y]
                    if diag_val < best_val:
                        self.target_tile = (diag_x, diag_y)
                        return

        # Fallback: go to best cardinal
        self.target_tile = best_cardinal[2]

    def _is_solid(self, gx, gy):
        """Check if a grid position is solid"""
        return (0 <= gx < self.level.grid_width and
                0 <= gy < self.level.grid_height and
                self.level.tile_grid[gy][gx] is not None)

    def flip_gravity(self):
        pass

    def attack(self):
        self.player.hit(self)

    def eliminate(self):
        super().eliminate()

    def render(self, screen, camera):
        render_pos = camera.apply(self)
        image = self.image

        rotated_image = pygame.transform.rotate(image, self.rotation_angle)
        rotated_rect = rotated_image.get_rect(center=(
            render_pos[0] + self.render_offset[0] + image.get_width() // 2,
            render_pos[1] + self.render_offset[1] + image.get_height() // 2
        ))

        screen.blit(rotated_image, rotated_rect.topleft)
        self.render_health_bar(screen, camera)

        # Debug box
        # pygame.draw.rect(screen, (255, 0, 0), camera.apply(self), 1)
