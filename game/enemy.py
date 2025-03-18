import json
import os
import pygame
from game.entities import Entity

count = 0

class Enemy(Entity):
    def __init__(self, x, y, width, height, scale):
        super().__init__(x, y, width * scale, height * scale)
        self.sprites = self.load_sprites()
        self.state = "idle"
        self.sprite_index = 0
        self.animation_speed = 0.1
        self.time_accumulator = 0
        self.facing_right = True
        self.speed = 40
        self.has_jumped = True

    def load_sprites(self):
        with open("assets/characters/player.json") as f:
            data = json.load(f)
        return {
            state: [pygame.transform.scale(
                        pygame.image.load(os.path.join("assets/characters", path)).convert_alpha(),
                        (self.rect.width, self.rect.height)
                    ) for path in paths]
            for state, paths in data.items()
        }

    def update(self, level, dt):
        new_state = "idle"

        if self.state == "idle":
            self.walk_up_and_down(level, dt)

        if self.velocity.y > 0 and (not self.has_jumped):
            self.jump(dt)
            self.has_jumped = True

        if self.on_ground and self.has_jumped:
            self.has_jumped = False

        super().update(level, dt)

        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity.x = 0
        if self.rect.right > level.width:
            self.rect.right = level.width
            self.velocity.x = 0

        self.update_animation(new_state, dt)

    def update_animation(self, new_state, dt):
        if new_state != "jump" and not self.on_ground:
            new_state = "jump"

        if new_state != self.state:
            self.state = new_state
            self.sprite_index = 0

        self.time_accumulator += dt
        if self.time_accumulator >= self.animation_speed:
            self.sprite_index = (self.sprite_index + 1) % len(self.sprites[self.state])
            self.time_accumulator = 0

    def walk_up_and_down(self, level, dt):
            
        if self.facing_right:
            if self.rect.right > level.width:
                self.rect.left = 0
                self.facing_right = False
            elif self.hit == True:
                self.facing_right = False
            else:
                self.velocity.x = self.speed * dt
        else:
            if self.rect.left < 0:
                self.rect.left = 0
                self.facing_right = True
            elif self.hit == True:
                self.facing_right = True
            else:
                self.velocity.x = -self.speed * dt
        
    def jump(self, dt):
        if self.velocity.x > 0:
            self.velocity.x += 0.1 * self.speed
        elif self.velocity.x < 0:
            self.velocity.x -= 0.1 * self.speed
        self.velocity.y = -50 * dt
        
            
    def eliminate(self):
        print("Player eliminated")
