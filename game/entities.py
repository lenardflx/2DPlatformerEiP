import json

import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_path, json_path, level, sound_manager):
        super().__init__()
        # Load sprite data first so we know the size and scale before creating the rect
        self.sound_manager = sound_manager
        self.sprites = {}
        self.state = "idle"
        self.last_state = "idle"
        self.sprite_index = 0
        self.animation_speed = 0.1
        self.time_accumulator = 0
        self.render_offset = (0, 0)
        self.hit_edge = False
        self.kb_x = 3
        self.kb_y = 2
        self.max_health = 6
        self.health = self.max_health
        self.apply_gravity = True

        self.sprite_data = None
        self.entity_size = [16, 16]
        self.scale = 1.0
        self.tile_size = None

        self.load_sprite_metadata(sprite_path, json_path)  # loads size & scale

        # Calculate scaled hitbox size
        width = self.entity_size[0] * self.scale
        height = self.entity_size[1] * self.scale
        self.rect = pygame.Rect(x, y, width, height)

        # Physics
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing_right = True
        self.is_flipped = False
        self.attacking = False
        self.stunned = False
        self.stun = 0

        # Fallback image (in case sprites are not loaded)
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0))

        # Actually load the sprites into memory
        self.load_sprites(sprite_path)

    def load_sprite_metadata(self, sprite_path, json_path):
        """Load metadata like entity_size and scale from the JSON config."""
        with open(json_path) as f:
            data = json.load(f)

        self.sprite_data = data
        self.entity_size = tuple(data.get("entity_size", [16, 16]))
        self.scale = data.get("entity_scale", 1.0)
        self.tile_size = data.get("tile_size", 16)

    def load_sprites(self, sprite_path):
        """Loads animations from a sprite sheet using already-loaded metadata."""
        sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
        scaled_size = int(self.tile_size * self.scale)

        for state, frames in self.sprite_data["animations"].items():
            self.sprites[state] = []
            for frame in frames:
                col, row = map(int, frame.split(","))
                x, y = col * self.tile_size, row * self.tile_size
                sprite = sprite_sheet.subsurface((x, y, self.tile_size, self.tile_size))
                sprite = pygame.transform.scale(sprite, (scaled_size, scaled_size))
                self.sprites[state].append(sprite)

        self.image = self.sprites[self.state][0]

        # Set render offset (centered horizontally, bottom aligned)
        x_off = (self.rect.width - scaled_size) // 2
        y_off = self.rect.height - scaled_size
        self.render_offset = (x_off, y_off)

    def update(self, level, dt):
        """Handles entity movement, physics, and animations."""
        if self.health <= 0:
            self.eliminate()
            return

        if self.stun > 0:
            self.stun -= 1

        if self.apply_gravity:
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

    def handle_collisions(self, level, direction):
        """Handles collisions with solid tiles in the given direction."""
        if direction == "horizontal":
            for tile in level.get_solid_tiles_near(self):
                if self.rect.colliderect(tile.rect):
                    if self.velocity.x > 0:  # Moving right
                        self.rect.right = tile.rect.left
                    elif self.velocity.x < 0:  # Moving left
                        self.rect.left = tile.rect.right
                    self.velocity.x = 0
                    self.hit_edge = True

        elif direction == "vertical":
            for tile in level.get_solid_tiles_near(self):
                if self.rect.colliderect(tile.rect):
                    if self.velocity.y > 0:     #Fall
                        self.rect.bottom = tile.rect.top
                        self.velocity.y = 0
                    elif self.velocity.y < 0:   #Jump
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
        """Renders the entity sprite with gravity-aware offset."""
        base_pos = camera.apply(self)
        x = base_pos[0] + self.render_offset[0]
        y = base_pos[1] if self.is_flipped else base_pos[1] + self.render_offset[1]

        screen.blit(self.image, (x, y))
        pygame.draw.rect(screen, (255, 0, 0), base_pos, 1) # Debug: show hitbox
        self.render_health_bar(screen,camera)

    def eliminate(self):
        """Removes the entity from the game."""
        self.health = 0
        self.kill()
        print(f"{self.__class__.__name__} eliminated")

    def render_health_bar(self, screen, camera):
        if self.health == self.max_health:
            return
        pos = camera.apply(self)
        if self.is_flipped:
            y = pos[1] + self.rect.height + 5
        else:
            y = pos[1] - 10
        x = pos[0]

        pygame.draw.rect(screen, (16,8,36), (x, y, self.rect.width, 3))
        health_width = self.health / self.max_health * self.rect.width
        pygame.draw.rect(screen, (60,160,255), (x, y, health_width, 3))

    def hit(self, attacker, stun=20):
        """Handles entity damage, knockback, and hit animation."""
        self.stun = stun
        self.health -= attacker.damage

        kb_x = getattr(attacker, "kb_x", 3)
        kb_y = getattr(attacker, "kb_y", 2)

        knockback_x = kb_x if self.rect.x > attacker.rect.x else -kb_x
        knockback_y = kb_y if self.is_flipped else -kb_y

        self.knockback(knockback_x, knockback_y)

    def knockback(self, x, y):
        self.on_ground = False
        
        self.velocity.x = x
        self.velocity.y = y