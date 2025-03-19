import json

import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()

        # Entity properties
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing_right = True
        self.state = "idle"
        self.is_flipped = False

        # Animation system
        self.sprites = {}
        self.sprite_index = 0
        self.animation_speed = 0.1
        self.time_accumulator = 0

        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0))  # Temporary red box (if sprite is missing)

    def load_sprites(self, sprite_path, json_path):
        """Loads animations from a sprite sheet and JSON mapping file."""
        with open(json_path) as f:
            data = json.load(f)

        sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
        tile_size = data["tile_size"]
        self.sprites = {}  # Store animations

        for state, frames in data["animations"].items():
            self.sprites[state] = []
            for frame in frames:
                col, row = map(int, frame.split(","))  # Get sprite position
                x, y = col * tile_size, row * tile_size
                sprite = sprite_sheet.subsurface((x, y, tile_size, tile_size))  # Extract sprite
                self.sprites[state].append(sprite)

        if "idle" in self.sprites:
            self.state = "idle"
        else:
            self.state = next(iter(self.sprites))

        self.sprite_index = 0
        self.image = self.sprites[self.state][self.sprite_index]  # Set initial sprite

    def update(self, level, dt):
        """Handles entity movement, physics, and animations."""
        self.velocity.y += level.gravity * dt  # Apply gravity
        self.move(level)
        self.update_animation(dt)

    def flip_gravity(self):
        """Flips the entity's sprite and inverts its vertical velocity."""
        self.velocity.y *= -1  # Invert falling direction
        self.on_ground = False  # Prevent instant ground snap
        self.is_flipped = not self.is_flipped

    def move(self, level):
        """Moves entity and resolves collisions using sweep-based checks."""
        self.on_ground = False

        # Move horizontally and check for collisions
        self.rect.x += self.velocity.x
        self.handle_collisions(level, direction="horizontal")

        # Move vertically and check for collisions
        self.rect.y += self.velocity.y
        self.handle_collisions(level, direction="vertical")

    def handle_collisions(self, level, direction):
        """Handles collisions with solid tiles in the given direction."""
        for tile in level.get_solid_tiles_near(self):
            if direction == "horizontal":
                if self.rect.colliderect(tile.rect):
                    if self.velocity.x > 0:  # Moving right
                        self.rect.right = tile.rect.left
                    elif self.velocity.x < 0:  # Moving left
                        self.rect.left = tile.rect.right
                    self.velocity.x = 0
            elif direction == "vertical":
                if self.rect.colliderect(tile.rect):
                    if self.velocity.y > 0 and level.gravity > 0:  # Falling Down
                        self.rect.bottom = tile.rect.top
                        self.on_ground = True
                    elif self.velocity.y < 0 and level.gravity < 0:  # Falling Up
                        self.rect.top = tile.rect.bottom
                        self.on_ground = True
                    self.velocity.y = 0

    def update_animation(self, dt):
        """Updates the entity's animation safely and efficiently."""
        frames = self.sprites.get(self.state, [])
        if not frames:
            return  # No frames available for this state

        # Ensure sprite_index is within range after switching states
        self.sprite_index = min(self.sprite_index, len(frames) - 1)

        self.time_accumulator += dt
        if self.time_accumulator >= self.animation_speed:
            self.time_accumulator -= self.animation_speed
            self.sprite_index = (self.sprite_index + 1) % len(frames)  # Cycle through frames

        # Update the current image
        self.image = frames[self.sprite_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.is_flipped:
            self.image = pygame.transform.flip(self.image, False, True)

    def render(self, screen, camera):
        """Renders the entity sprite."""
        if self.sprites:
            sprite = self.sprites[self.state][self.sprite_index]
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            screen.blit(sprite, camera.apply(self))

    def eliminate(self):
        """Removes the entity from the game."""
        print(f"{self.__class__.__name__} eliminated")