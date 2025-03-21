import json

import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, scale=1):
        super().__init__()
        width *= scale
        height *= scale

        # Entity properties
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing_right = True
        self.is_flipped = False
        self.state = "idle"
        self.last_state = "idle"
        self.attacking = False
        self.stunned = False

        # Render system
        self.sprites = {}
        self.sprite_index = 0
        self.animation_speed = 0.1
        self.time_accumulator = 0
        self.scale = scale
        self.render_offset = (0, 0)

        self.stun = 0

        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0))  # Temporary red box (if sprite is missing)

    def load_sprites(self, sprite_path, json_path):
        """Loads animations from a sprite sheet and JSON mapping file."""
        with open(json_path) as f:
            data = json.load(f)

        sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
        tile_size = data["tile_size"]
        scaled_size = int(tile_size * self.scale)
        self.sprites = {}  # Store animations

        for state, frames in data["animations"].items():
            self.sprites[state] = []
            for frame in frames:
                col, row = map(int, frame.split(","))  # Get sprite position
                x, y = col * tile_size, row * tile_size
                sprite = sprite_sheet.subsurface((x, y, tile_size, tile_size))  # Extract sprite
                sprite = pygame.transform.scale(sprite, (scaled_size, scaled_size))
                self.sprites[state].append(sprite)

        self.sprite_index = 0
        self.image = self.sprites[self.state][self.sprite_index]  # Set initial sprite

        # set render offset (horizontal centering, vertical bottom)
        x_off = (self.rect.width - scaled_size) // 2
        y_off = self.rect.height - scaled_size
        self.render_offset = (x_off, y_off)

    def update(self, level, dt):
        """Handles entity movement, physics, and animations."""
        if self.stun > 0:
            self.stun -= 1

        self.velocity.y += level.gravity * dt  # Apply gravity
        self.move(level)
        self.update_animation(dt)

        # Check if out of bounds
        if (not self.is_flipped and self.rect.top > level.height) or (self.is_flipped and self.rect.bottom < 0):
            self.eliminate()

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

    def handle_collisions(self, level, direction, ground_buffer=1):
        """Handles collisions with solid tiles in the given direction."""
        if direction == "horizontal":
            for tile in level.get_solid_tiles_near(self):
                if self.rect.colliderect(tile.rect):
                    if self.velocity.x > 0:  # Moving right
                        self.rect.right = tile.rect.left
                    elif self.velocity.x < 0:  # Moving left
                        self.rect.left = tile.rect.right
                    self.velocity.x = 0

        elif direction == "vertical":
            for tile in level.get_solid_tiles_near(self):
                if self.rect.colliderect(tile.rect):
                    if self.velocity.y > 0 and level.gravity > 0:
                        self.rect.bottom = tile.rect.top
                        self.velocity.y = 0
                    elif self.velocity.y < 0 and level.gravity < 0:
                        self.rect.top = tile.rect.bottom
                        self.velocity.y = 0

        # Always check for grounding (secondary contact check)
        self.check_if_grounded(level)

    def check_if_grounded(self, level):
        """Ensures on_ground is true when standing on something."""
        self.on_ground = False  # Reset

        feet_rect = self.rect.copy()
        buffer = 1  # Slight overlap below feet

        if level.gravity > 0:
            feet_rect.y += buffer
        else:
            feet_rect.y -= buffer

        for tile in level.get_solid_tiles_near(self):
            if feet_rect.colliderect(tile.rect):
                self.on_ground = True
                return

    def update_animation(self, dt):
        """Updates the entity's animation safely and efficiently."""
        frames = self.sprites.get(self.state, [])
        if not frames:
            return  # No frames available for this state

        if self.state != self.last_state:
            self.sprite_index = 0
            self.last_state = self.state

        self.time_accumulator += dt
        if self.time_accumulator >= self.animation_speed:
            self.time_accumulator -= self.animation_speed
            if self.state in ["jump", "attack", "take_dmg"]:
                if self.sprite_index < len(frames) - 1:
                    self.sprite_index += 1  # Progress animation normally
            else:
                self.sprite_index = (self.sprite_index + 1) % len(frames)  # Loop animation

        # Apply flipped transformations
        self.image = frames[self.sprite_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.is_flipped:
            self.image = pygame.transform.flip(self.image, False, True)

    def set_state(self, new_state):
        """Safely switches states and resets animations."""
        if new_state == self.state:
            return
        if self.state not in ["attack", "take_dmg"]:  # Prevent overriding mid-attack/damage
            self.last_state = self.state  # Store last valid movement state
        self.state = new_state
        self.sprite_index = 0  # Reset animation frame

    def render(self, screen, camera):
        """Renders the entity sprite at the correct position with an offset."""
        render_pos = camera.apply(self)  # Get position from camera
        screen.blit(self.image, (render_pos[0] + self.render_offset[0],
                                 render_pos[1] + self.render_offset[1]))

    def eliminate(self):
        """Removes the entity from the game."""
        print(f"{self.__class__.__name__} eliminated")

    def hit(self, attacker):
        """Handles entity damage, knockback, and hit animation."""
        self.stun = 20

        knockback_x = 3 if self.rect.x > attacker.rect.x else -3
        knockback_y = 2 if self.is_flipped else -2

        self.velocity.x = knockback_x
        self.velocity.y = knockback_y