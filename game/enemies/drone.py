import math
import pygame
from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("drone")
class Drone(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level):
        super().__init__(x, y, sprite_path, json_path, level)
        self.player = player
        self.level = level
        self.speed = 60
        self.damage = 1
        self.health = 6
        self.kb_x = 3
        self.kb_y = 2
        self.detection_range = 12 * level.tile_size

        self.direction = pygame.Vector2(0, 0)
        self.smoothing = 0.2
        self.rotation_angle = 0

        # Attack logic
        self.charge_cooldown = 0
        self.charge_duration = 0
        self.windup_timer = 0
        self.in_charge = False

        # Behavior tweaks
        self.overhead_offset = -40  # Hover height above player
        self.attack_range = 30      # Vertical trigger range to drop

    def update(self, level, dt):
        distance = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)

        if self.charge_cooldown > 0:
            self.charge_cooldown -= 1

        if self.in_charge:
            self.charge_duration -= 1
            if self.charge_duration <= 0:
                self.in_charge = False
                self.velocity = pygame.Vector2(0, 0)
        elif distance < self.detection_range and not self.stun:
            self.smart_chase(dt)
            self.state = "run"
        else:
            self.velocity *= 0.9  # slow down
            self.state = "idle"

        # Rotation toward player (limited to slight tilts)
        dx = self.player.rect.centerx - self.rect.centerx
        max_angle = 20
        self.rotation_angle = max(-max_angle, min(max_angle, dx * 0.1))

        # Directional flip (for animation)
        self.facing_right = dx >= 0

        super().update(level, dt)

        # Attack check
        if self.rect.colliderect(self.player.rect):
            self.attack()

    def smart_chase(self, dt):
        """Drone tries to maintain high ground and attack if possible."""
        player_head = pygame.Vector2(self.player.rect.centerx, self.player.rect.top)
        drone_pos = pygame.Vector2(self.rect.centerx, self.rect.centery)

        to_target = (player_head + pygame.Vector2(0, self.overhead_offset)) - drone_pos
        dist_to_player = drone_pos.distance_to(player_head)

        # Charge logic
        vertical_aligned = abs(self.rect.centerx - self.player.rect.centerx) < 10
        should_charge = dist_to_player < 100 and vertical_aligned and self.charge_cooldown == 0

        if should_charge:
            if self.windup_timer < 20:
                self.windup_timer += 1
                self.velocity *= 0.95  # pause before charge
            else:
                self.in_charge = True
                self.charge_duration = 20
                self.charge_cooldown = 90
                self.windup_timer = 0

                charge_vector = (player_head - drone_pos).normalize()
                self.velocity = charge_vector * (self.speed * 2)
        else:
            # Smooth flight above player
            if to_target.length_squared() > 4:
                to_target = to_target.normalize()
                self.direction = self.direction.lerp(to_target, self.smoothing)

            base_speed = self.speed * dt
            self.velocity.x = self.direction.x * base_speed

            # Stay slightly higher unless aligned
            if vertical_aligned:
                self.velocity.y = self.direction.y * base_speed
            else:
                if self.rect.centery > player_head.y + self.overhead_offset:
                    self.velocity.y = -base_speed * 0.6
                else:
                    self.velocity.y = 0

    def attack(self):
        self.player.hit(self)

    def eliminate(self):
        print("Drone eliminated")
        self.kill()

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
