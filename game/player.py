import pygame

from game.entities import Entity

class Player(Entity):
    def __init__(self, x, y, width, height, scale, controls):
        super().__init__(x, y, width * scale, height * scale)
        self.controls = controls

        # Player attributes
        self.max_health = 6
        self.health = self.max_health
        self.coins = 0
        self.speed = 120
        self.jump_strength = -100  # Base jump force
        self.jump_hold_force = -20  # Additional force while holding jump
        self.max_jump_countdown = 6  # Maximum frames to hold jump
        self.jump_countdown = self.max_jump_countdown
        self.hitstun = 0

        # Animation flags
        self.is_jumping = False
        self.jump_anim_done = False
        self.attack_cooldown = 0
        self.attack_active = False
        self.damage_anim_active = False

        self.is_jumping = False
        self.got_hit = (0, 0, 0)

        self.load_sprites("assets/characters/player.png", "assets/characters/player.json")

    def update(self, level, dt):
        """Handles player movement, physics, and animations."""
        if self.health <= 0:
            self.eliminate()
            return

        if self.hitstun > 0:
            self.hitstun -= 1
        if self.stun > 0:
            self.stun -= 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

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
        left = self.controls.is_action_active("move_left")
        right = self.controls.is_action_active("move_right")

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

        # Handle taking damage
        if not self.got_hit == (0,0,0):
            self.get_hit()

        # Handle jumping (hold jump for higher jumps)
        jump_pressed = self.controls.is_action_active("jump")
        jump_direction = -1 if self.is_flipped else 1  # Flip jump when gravity is inverted

        if jump_pressed and not self.attack_active:
            if self.on_ground:
                self.velocity.y = self.jump_strength * dt * jump_direction  # Initial jump
                self.is_jumping = True
                self.jump_anim_done = False  # ✅ Reset jump animation flag
                self.on_ground = False
                self.jump_countdown = self.max_jump_countdown
                new_state = "jump"
            elif self.is_jumping and self.jump_countdown > 0:
                self.velocity.y += self.jump_hold_force * dt * jump_direction
                self.jump_countdown -= 1

        # ✅ Handle Jump Animation
        if self.is_jumping:
            if not self.jump_anim_done:
                new_state = "jump"  # Play jump animation
                if self.sprite_index >= len(self.sprites["jump"]) - 1:
                    self.jump_anim_done = True  # ✅ Lock to last frame
            else:
                new_state = "jump"  # Keep last frame

        # ✅ Reset Jump Animation on Landing
        if self.on_ground and self.is_jumping:
            self.is_jumping = False
            self.jump_anim_done = False  # ✅ Reset animation lock

        # ✅ Handle Attacking (LEFT-CLICK)
        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            if self.attack_cooldown == 0 and not self.attack_active:
                self.attack_active = True
                self.attack_cooldown = 20  # Cooldown after attack
                self.sprite_index = 0  # Reset animation
                new_state = "attack"

        # ✅ Attack Animation Handling
        if self.attack_active:
            new_state = "attack"
            if self.sprite_index >= len(self.sprites["attack"]) - 1:
                self.attack_active = False  # ✅ End attack after animation

        super().update(level, dt)  # Apply physics and collision
        self.state = new_state  # Update state for animation

    def get_hit(self):
        """Handles player damage and knockback, then plays the damage animation fully."""
        if self.hitstun == 0:
            self.health -= self.got_hit[0]
            self.hitstun = self.got_hit[1]
            self.stun = 30
            if self.facing_right:
                self.velocity.x = -self.got_hit[2]
            else:
                self.velocity.x = self.got_hit[2]
            self.velocity.y = -2


            #self.damage_anim_active = True
            #self.sprite_index = 0
            #self.state = "take_dmg"

        self.got_hit = (0, 0, 0)
