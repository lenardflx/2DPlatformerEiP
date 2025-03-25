import pygame

from game.entities import Entity
import game.abilities as abilities
from game.menu.menu_state import MenuState


class Player(Entity):
    def __init__(self, x, y, sprite_path, json_path, controls, level, sound_manager):
        super().__init__(x, y, sprite_path, json_path, level, sound_manager)
        self.controls = controls

        # Player attributes
        self.max_health = 6
        self.health = self.max_health
        self.damage = 1
        self.coins = 0
        self.base_speed = 100 * self.scale
        self.speed = self.base_speed
        self.kb_x = 2
        self.kb_y = 1
        self.controls_inverted = False
        self.invert_timer = 0

        # Charge Parameters
        self.charge_speed = 0.3 * self.base_speed
        self.charge = 0
        self.max_charge = 100
        self.min_charge_display = 5
        self.charge_bar_width = 8
        self.charge_bar_height = 20

        # Jumping attributes
        self.jump_was_released = True
        self.jump_strength = -50 * self.scale
        self.jump_hold_force = -15 * self.scale
        self.max_jump_countdown = 7
        self.jump_countdown = self.max_jump_countdown

        # Animation flags
        self.flicker = 0
        self.immunity_frames = 0
        self.is_jumping = False
        self.jump_anim_done = False
        self.attack_cooldown = 0
        self.attack_active = False
        self.damage_anim_active = False

        self.is_jumping = False

        # Abilities
        self.abilities_blocked = False
        self.level = level
        self.player_dt = 0
        self.abilities = {
            "double_jump": abilities.DoubleJumpAbility(level, self),
            "gravity_inverse": abilities.GravityInverseAbility(level, self),
        }

        # Death Screen
        self.show_death_screen = False
        self.death_screen_cooldown = 50

    def update(self, level, dt):
        """Handles player movement, physics, and animations."""
        if self.health <= 0:
            self.eliminate()
            self.death_screen_cooldown -= 1
            if self.death_screen_cooldown <= 0:
                self.show_death_screen = True
            return
        self.player_dt = dt

        if self.invert_timer > 0:
            self.invert_timer -= dt
            if self.invert_timer < 0:
                self.invert_timer = 0
        if self.invert_timer == 0:
            self.controls_inverted = False

        if self.immunity_frames > 0:
            self.immunity_frames -= 1
            # Flicker AFTER the hit animation is done
            self.flicker = not self.damage_anim_active or (self.immunity_frames % 6 < 3)
        else:
            self.flicker = False  # No flicker after immunity ends

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        for ability in self.abilities.values():
            ability.update()

        new_state = "idle"

        # Play damage animation fully before resuming control
        if self.damage_anim_active and not self.damage_anim_active: # aktuell deaktiviert
            if self.sprite_index >= len(self.sprites["take_dmg"]) - 1:
                self.damage_anim_active = False  # End damage animation
            else:
                return  # Skip movement & actions during damage animation

        # Stop movement when on ground
        if self.on_ground:
            self.velocity.x = 0

        # Handle movement
        if not self.controls_inverted:
            left = self.controls.is_action_active("move_left")
            right = self.controls.is_action_active("move_right")
        else:
            left = self.controls.is_action_active("move_right")
            right = self.controls.is_action_active("move_left")

        if self.stun == 0 and not self.attack_active:
            if left and right:
                new_state = "idle"
            elif left:
                self.velocity.x = -self.speed * dt
                self.facing_right = False
                new_state = "run"
            elif right:
                self.velocity.x = self.speed * dt
                self.facing_right = True
                new_state = "run"

        # Handle jumping (hold jump for higher jumps)
        jump_pressed = self.controls.is_action_active("jump")
        jump_direction = -1 if self.is_flipped else 1  # Flip jump when gravity is inverted

        # Jump
        perform_start_jump = False
        if jump_pressed and not self.attack_active:
            if self.on_ground:
                perform_start_jump = True
            elif self.is_jumping and self.jump_countdown > 0 and not self.jump_was_released:
                # Hold to jump higher
                self.velocity.y += self.jump_hold_force * dt * jump_direction
                self.jump_countdown -= 1
            elif (
                    not self.on_ground and
                    self.jump_was_released and
                    self.abilities["double_jump"].can_activate()
                ):
                perform_start_jump = True
                self.abilities["double_jump"].activate()

        if perform_start_jump:
            self.velocity.y = self.jump_strength * dt * jump_direction
            self.jump_countdown = self.max_jump_countdown
            self.is_jumping = True
            self.jump_anim_done = False
            self.jump_was_released = False
            self.on_ground = False
            new_state = "jump"

        # Release Jump
        if not jump_pressed:
            self.jump_was_released = True

        # Handle Jump Animation
        if self.is_jumping:
            if not self.jump_anim_done:
                new_state = "jump"  # Play jump animation
                if self.sprite_index >= len(self.sprites["jump"]) - 1:
                    self.jump_anim_done = True  # Lock to last frame
            else:
                new_state = "jump"  # Keep last frame

        # Reset Jump Animation on Landing
        if self.on_ground and self.is_jumping:
            self.is_jumping = False
            self.jump_anim_done = False  # Reset animation lock

        # Handle Attacking (LEFT-CLICK)
        if pygame.mouse.get_pressed()[0] and not self.attack_cooldown:
            self.charge = min(self.charge + 1, self.max_charge)
            self.speed = self.charge_speed
            new_state = "charge"
        elif self.charge > 0:
            self.speed = self.base_speed
            self.attack_active = True
            self.attack_cooldown = 20 + self.charge // 2
            self.damage = 1 + self.charge // 25
            self.charge = 0
            self.sprite_index = 0
            new_state = "attack"
            self.perform_attack(level)

        # Attack Animation Handling
        if self.attack_active:
            new_state = "attack"
            if self.sprite_index >= len(self.sprites["attack"]) - 1:
                self.attack_active = False  # End attack after animation

        # Gravity Ability
        if self.controls.is_action_active("gravity_inverse"):
            self.abilities["gravity_inverse"].activate()

        super().update(level, dt)  # Apply physics and collision

        # Check if player center touches right screen edge
        if self.rect.centerx >= level.width:
            level.engine.menu.open_menu(MenuState.COMPLETE, level.engine, level)

        self.state = new_state  # Update state for animation

    def perform_attack(self, level):
        """Creates an attack hitbox and eliminates enemies inside it."""
        self.sound_manager.play_sfx("basic_attack")

        attack_width = self.rect.width * 0.75
        attack_height = self.rect.height * 0.5
        attack_x = self.rect.right if self.facing_right else self.rect.left - attack_width
        attack_y = self.rect.top

        attack_rect = pygame.Rect(attack_x, attack_y, attack_width, attack_height)

        # Check collision with enemies
        for enemy in level.enemies:
            if attack_rect.colliderect(enemy.rect):
                enemy.hit(self)


    def hit(self, attacker, stun=30):
        """Handles player damage, knockback, and hit animation."""
        if self.immunity_frames == 0:
            self.immunity_frames = 40

            super().hit(attacker, stun)

            # Activate hit animation
            self.state = "take_dmg"
            self.damage_anim_active = True
            self.sprite_index = 0  # Start damage animation

    def render(self, screen, camera):
        """Renders the player on the screen."""
        if self.flicker:
            return
        super().render(screen, camera)
        self.draw_charge_bar(screen, camera)

    def draw_charge_bar(self, screen, camera):
        """Draws the player's charge bar beside the player, centered to their body height."""
        if self.charge > self.min_charge_display:
            pos = camera.apply(self)
            y = pos[1] - self.charge_bar_height + self.rect.height // 2
            x = pos[0] - self.charge_bar_width - 5 if self.facing_right else pos[0] + self.rect.width + 5
            filled_height = self.charge / self.max_charge * self.charge_bar_height

            pygame.draw.rect(screen, (16,8,36), (x, y, self.charge_bar_width, self.charge_bar_height))
            pygame.draw.rect(screen, (255,233,70),
                             (x, y + self.charge_bar_height - filled_height, self.charge_bar_width, filled_height))

    def invert_controls(self):
        self.controls_inverted = not self.controls_inverted
        self.invert_timer = 6

    def eliminate(self):
        """Handles player elimination (game over)."""
        self.health = 0
