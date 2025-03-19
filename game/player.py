import json
import os
import pygame
from core.controls import Controls
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
        self.jump_strength = -200
        self.jump_cut_multiplier = 0.2
        self.hitstun = 0
        self.is_jumping = False

        self.load_sprites("assets/characters/player.png", "assets/characters/player.json")

    def update(self, level, dt):
        """Handles player movement, physics, and animations."""
        if self.health <= 0:
            self.eliminate()
            return

        if self.hitstun > 0:
            self.hitstun -= 1

        # Reset movement
        self.velocity.x = 0
        new_state = "idle"

        # Handle movement
        left = self.controls.is_action_active("move_left")
        right = self.controls.is_action_active("move_right")

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
        jump_direction = -1 if self.is_flipped else 1  # ✅ Flip jump direction when gravity is flipped

        if jump_pressed and self.on_ground:
            self.velocity.y = self.jump_strength * dt * jump_direction  # ✅ Jump in correct direction
            self.is_jumping = True
            new_state = "jump"

        elif not jump_pressed and self.is_jumping:
            if (not self.is_flipped and self.velocity.y < 0) or (self.is_flipped and self.velocity.y > 0):
                self.velocity.y *= self.jump_cut_multiplier  # ✅ Jump cut-off works in both gravity states
            self.is_jumping = False

        # Reset jump state when landing
        if self.on_ground:
            self.is_jumping = False

        super().update(level, dt)  # Apply physics and collision
        self.state = new_state  # Update state for animation

    def get_hit(self, damage, duration, knockback=0):
        """Handles player damage and knockback."""
        if self.hitstun == 0:
            self.health -= damage
            self.hitstun = duration
            self.velocity.x += knockback if not self.facing_right else -knockback
