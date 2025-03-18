import json
import os
import pygame
from game.entities import Entity



class Player(Entity):
    def __init__(self, x, y, width, height, scale):
        super().__init__(x, y, width * scale, height * scale)
        self.sprites = self.load_sprites()
        self.state = "idle"
        self.sprite_index = 0
        self.animation_speed = 0.1
        self.time_accumulator = 0
        self.facing_right = True
    maxjump = 12
    jump_count = 0

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
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        new_state = "idle"

        if keys[pygame.K_LEFT]:
            self.velocity.x = -100 * dt
            new_state = "run"
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.velocity.x = 100 * dt
            new_state = "run"
            self.facing_right = True
        
        #Jump higher or lower
        if keys[pygame.K_SPACE]:
            if self.on_ground or self.jump_count < self.maxjump:
                self.velocity.y = -100 * dt
                new_state = "jump"
        elif not self.on_ground:
            self.jump_count = self.maxjump
            
        if (not self.on_ground) and self.jump_count < self.maxjump:
            self.jump_count += 1

        if self.on_ground and self.jump_count != 0:
            self.jump_count = 0

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

    def eliminate(self):
        print("Player eliminated")
