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
        self.y_gun_offset = 4
        self.beam_duration = 10
        self.beam_timer = 0
        self.beam_start = None
        self.beam_end = None

        self.rotation_angle = 0
        self.rotation_speed_deg = 3

        # Preload assets
        self.turret_base = pygame.image.load("assets/characters/turret_base.png").convert_alpha()
        self.rect.y -= 0.28 * self.level.tile_size

        # Cache rotated sprites
        self.sprite_cache = {}
        self.precompute_rotated_sprites()

    def precompute_rotated_sprites(self):
        """Precompute rotated sprites to avoid real-time rotation"""
        for state in self.sprites:
            self.sprite_cache[state] = []
            for frame in self.sprites[state]:
                rotations = {}
                # Cache at 15-degree increments for less memory usage
                for angle in range(0, 360, 5):
                    rotated = pygame.transform.rotate(frame, angle)
                    rotations[angle] = rotated
                self.sprite_cache[state].append(rotations)

    def get_cached_sprite(self, state, frame_idx, angle):
        """Retrieve nearest precomputed sprite"""
        nearest_angle = round(angle / 5) * 5 % 360
        return self.sprite_cache[state][frame_idx][nearest_angle]

    def flip_gravity(self):
        pass

    def update(self, level, dt):
        if self.health <= 0:
            self.eliminate()
            return

        self.facing_right = self.player.rect.x >= self.rect.x

        distance = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)
        in_range = distance <= self.attack_range and self.line_of_sight()

        if self.state == "attack":
            if self.sprite_index >= len(self.sprites["attack"]) - 1:
                self.set_state("shoot")

        elif self.state == "shoot":
            self.shoot()
            self.beam_timer = self.beam_duration
            if self.sprite_index >= len(self.sprites["shoot"]) - 1:
                self.current_cooldown = self.cooldown
                self.set_state("await")

        elif self.state == "await":
            self.current_cooldown -= 1
            if self.current_cooldown <= 0:
                self.set_state("idle")
            else:
                if in_range:
                    self.rotate_towards_player()

        elif self.state == "idle":
            if in_range and self.current_cooldown <= 0:
                self.set_state("attack")
            else:
                self.rotate_towards_player()
                self.current_cooldown = max(0, self.current_cooldown - 1)

        if self.beam_timer > 0:
            self.beam_timer -= 1

        self.velocity = pygame.Vector2(0, 0)
        self.update_animation(dt)

    def rotate_towards_player(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        target_angle = math.degrees(math.atan2(-dy, dx)) % 360

        current = self.rotation_angle % 360
        diff = (target_angle - current + 540) % 360 - 180

        # Smooth rotation with dt for frame-rate independence
        rotation_step = self.rotation_speed_deg * (1 if diff > 0 else -1)
        if abs(diff) < abs(rotation_step):
            self.rotation_angle = target_angle
        else:
            self.rotation_angle += rotation_step

    def shoot(self):
        center = pygame.Vector2(self.rect.center)
        angle_rad = math.radians(self.rotation_angle)

        gun_length = self.rect.width // 2
        dx = math.cos(angle_rad)
        dy = -math.sin(angle_rad)

        self.beam_start = (
            center.x + dx * gun_length,
            center.y + dy * gun_length + self.y_gun_offset
        )
        self.beam_end = self.find_wall_from_center(self.rotation_angle)

        if self.player.rect.clipline(self.beam_start, self.beam_end):
            self.player.hit(self)

    def find_wall_from_center(self, angle_deg):
        """Optimized raycast with larger steps"""
        origin = pygame.Vector2(self.rect.center)
        direction = pygame.Vector2(math.cos(math.radians(angle_deg)), -math.sin(math.radians(angle_deg)))
        step = self.level.tile_size  # Larger step size to reduce checks
        max_distance = self.level.tile_size * 10  # Reduced max distance

        current_distance = 0
        while current_distance < max_distance:
            point = origin + direction * current_distance
            tile = self.level.get_tile_at(point.x, point.y)
            if tile and tile.solid:
                return point.x, point.y
            current_distance += step

        return (origin + direction * max_distance).x, (origin + direction * max_distance).y

    def line_of_sight(self):
        """Optimized line-of-sight with fewer checks"""
        start = pygame.Vector2(self.rect.center)
        end = pygame.Vector2(self.player.rect.center)
        if (end - start) == 0:
            return False
        direction = (end - start).normalize()
        distance = start.distance_to(end)
        step_size = self.level.tile_size * 2  # Larger step size
        steps = int(distance // step_size) + 1

        for i in range(1, steps):
            point = start + direction * (i * step_size)
            if point.distance_to(start) > distance:
                break
            tile = self.level.get_tile_at(point.x, point.y)
            if tile and tile.solid:
                return False
        return True

    def render(self, screen, camera):
        base_pos = camera.apply(self)

        # Draw base
        base_x = base_pos[0] + self.rect.width // 2 - self.turret_base.get_width() // 2
        base_y = base_pos[1] + self.rect.height - self.turret_base.get_height()
        screen.blit(self.turret_base, (base_x, base_y))

        # Draw rotated gun using cached sprite
        frame_idx = self.sprite_index
        state = self.state
        rotated = self.get_cached_sprite(state, frame_idx, self.rotation_angle)

        if not self.facing_right:
            rotated = pygame.transform.flip(rotated, False, True)

        rotated_rect = rotated.get_rect(center=camera.apply(self.rect).center)
        screen.blit(rotated, rotated_rect)

        # Optimized beam rendering (single line)
        if self.beam_timer > 0 and self.beam_start and self.beam_end:
            start = camera.apply(pygame.Rect(self.beam_start, (0, 0))).center
            end = camera.apply(pygame.Rect(self.beam_end, (0, 0))).center
            pygame.draw.line(screen, (100, 150, 255), start, end, self.level.tile_size // 4)

        self.render_health_bar(screen, camera)