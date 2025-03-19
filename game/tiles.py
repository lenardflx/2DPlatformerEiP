import pygame

# Global registry for all tile types
TILE_CLASSES = {}


def register_tile(tile_type):
    """Decorator to register a tile class by its type string."""

    def wrapper(cls):
        TILE_CLASSES[tile_type] = cls
        return cls

    return wrapper

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_info, tileset, tile_size=16):
        super().__init__()

        # Extract tile metadata
        self.index = tile_info["index"]
        self.collision_type = tile_info["collision_type"]
        self.tile_type = tile_info["type"]
        self.hitbox_data = tile_info.get("hitbox", {"width": 1.0, "height": 1.0})
        self.metadata = tile_info.get("metadata", {})

        # Determines if this tile needs updating every frame
        self.update_required = False

        # Compute texture position from index
        tiles_per_row = tileset.get_width() // tile_size
        texture_x = (self.index % tiles_per_row) * tile_size
        texture_y = (self.index // tiles_per_row) * tile_size

        # Extract texture from tile_set
        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.image.blit(tileset, (0, 0), (texture_x, texture_y, tile_size, tile_size))

        # Position and hitbox
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.solid = self.collision_type in ["solid", "platform"]

    def update(self, level):
        """Override in subclasses if needed"""
        pass


@register_tile("moving_platform")
class MovingPlatform(Tile):
    def __init__(self, x, y, tile_info, tileset, tile_size=16):
        super().__init__(x, y, tile_info, tileset, tile_size)

        self.update_required = True  # Ensure the platform updates every frame

        self.speed = self.metadata.get("speed", 1)
        self.direction = self.metadata.get("direction", "horizontal")
        self.movement_direction = 1  # 1 = forward, -1 = reverse
        self.tile_size = tile_size  # Tile size reference for movement

    def update(self, engine):
        """Moves the platform and interacts with the player + enemies."""
        level = engine.level
        player = engine.player
        next_x, next_y = self.rect.x, self.rect.y

        if self.direction == "horizontal":
            next_x += self.speed * self.movement_direction
            check_rect = pygame.Rect(
                next_x + (self.rect.width if self.movement_direction > 0 else -1),
                self.rect.y, 1, self.rect.height
            )  # ✅ Only check in movement direction (left/right)
        else:
            next_y += self.speed * self.movement_direction
            check_rect = pygame.Rect(
                self.rect.x,
                next_y + (self.rect.height if self.movement_direction > 0 else -1),
                self.rect.width, 1
            )  # ✅ Only check in movement direction (up/down)

        # Check for solid collisions
        blocked = any(tile.rect.colliderect(check_rect) for tile in level.get_solid_tiles_near(self))

        if blocked:
            self.movement_direction *= -1  # Reverse direction
            return  # Stop movement this frame

        # Move platform if no collision
        delta_x = next_x - self.rect.x
        delta_y = next_y - self.rect.y
        self.rect.x, self.rect.y = next_x, next_y

        # ✅ Carry entities smoothly
        for entity in [player] + list(level.enemies):  # ✅ Convert Group to List
            if (
                    entity.rect.bottom == self.rect.top  # ✅ Standing exactly on the platform
                    and entity.velocity.y >= 0  # ✅ Ensures they are not jumping
            ):
                entity.rect.y += delta_y  # Move up/down with platform
                entity.rect.x += delta_x  # Stick horizontally
                entity.velocity.x = delta_x  # Sync velocity for smooth movement

            # ✅ Push entities left or right if colliding from the sides
            elif self.movement_direction > 0 and entity.rect.left < self.rect.right <= entity.rect.left + abs(delta_x):
                entity.rect.left = self.rect.right  # Pushed from right

            elif self.movement_direction < 0 and entity.rect.right > self.rect.left >= entity.rect.right - abs(delta_x):
                entity.rect.right = self.rect.left  # Pushed from left

