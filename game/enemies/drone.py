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
        self.detection_range = 8 * level.tile_size

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
        """Drone tries to maintain high ground and attack if possible."""
        player_head = pygame.Vector2(self.player.rect.centerx, self.player.rect.top + 1)
        drone_pos = pygame.Vector2(self.rect.centerx, self.rect.centery)

        dist_to_player = drone_pos.distance_to(player_head)

        # Charge logic
        vertical_aligned = abs(self.rect.centerx - self.player.rect.centerx) < 10

        self.should_charge = dist_to_player < 100 and vertical_aligned and self.charge_cooldown == 0

        if self.should_charge:
            if self.windup_timer < 20:
                self.windup_timer += 1
                self.velocity *= 0.95  # pause before charge
            else:
                self.in_charge = True
                self.charge_duration = 20
                self.charge_cooldown = 90
                self.windup_timer = 0

                charge_vector = (player_head - drone_pos).normalize()
                self.velocity = charge_vector * (self.speed * 2) * dt
        else:
            # Get Closer To Player
            closest = 1000
            check = [[-1,0],[1,0],[0,-1],[0,1]]
            x = int(self.rect.centerx / 32)
            y = int(self.rect.centery / 32)
            space = [x, y]
            for c in check:
                x_new = x + c[0]
                y_new = y + c[1]
                try:
                    check = self.level.mp[x_new][y_new]
                except:
                    pass
                if check != None and check.size > 0 :
                    if check < closest:
                        closest = check
                        space = [x_new * 32, y_new * 32]
            if closest == 1000:
                self.state = "idle"
            else:
                if space[0] > self.rect.centerx:
                    self.velocity.x = self.speed * dt
                elif space[0] < self.rect.centerx:
                    self.velocity.x = -self.speed * dt
                elif space[1] > self.rect.centery:
                    self.velocity.y = self.speed * dt
                elif space[1] < self.rect.centery:
                    self.velocity.y = -self.speed * dt

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
