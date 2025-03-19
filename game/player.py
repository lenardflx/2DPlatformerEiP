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
        self.jump_strength = -100  # Base jump force
        self.jump_hold_force = -20  # Additional force while holding jump
        self.max_jump_countdown = 6  # Maximum frames to hold jump
        self.jump_countdown = self.max_jump_countdown
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
        jump_direction = -1 if self.is_flipped else 1  # Flip jump when gravity is inverted

        if jump_pressed:
            if self.on_ground:
                self.velocity.y = self.jump_strength * dt * jump_direction  # Initial jump
                self.is_jumping = True
                self.on_ground = False
                self.jump_countdown = self.max_jump_countdown
                new_state = "jump"
            elif self.is_jumping and self.jump_countdown > 0:
                self.velocity.y += self.jump_hold_force * dt * jump_direction
                self.jump_countdown -= 1

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
