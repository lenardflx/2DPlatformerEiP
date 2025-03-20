import pygame
from game.tiles.tiles_register import register_tile


@register_tile("block")
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_info, tile_set, tile_size):
        super().__init__()

        # Extract tile metadata
        self.index = tile_info["index"]
        self.collision_type = tile_info["collision_type"]
        self.tile_type = tile_info["type"]
        self.metadata = tile_info.get("metadata", {})

        # Extract tile hitbox
        hitbox = tile_info.get("hitbox", {"width": 1.0, "height": 1.0, "offset_x": 0.0, "offset_y": 0.0})
        self.hitbox_width = hitbox.get("width", 1.0) * tile_size
        self.hitbox_height = hitbox.get("height", 1.0) * tile_size
        self.hitbox_offset_x = hitbox.get("offset_x", 0.0) * tile_size
        self.hitbox_offset_y = hitbox.get("offset_y", 0.0) * tile_size

        # Determines if this tile needs updating every frame
        self.update_required = False

        # Compute texture position from index
        tiles_per_row = tile_set.get_width() // tile_size
        texture_x = (self.index % tiles_per_row) * tile_size
        texture_y = (self.index // tiles_per_row) * tile_size

        # Extract texture from tile_set
        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.image.blit(tile_set, (0, 0), (texture_x, texture_y, tile_size, tile_size))

        # Position and hitbox
        self.rect = pygame.Rect(
            x + self.hitbox_offset_x,
            y + self.hitbox_offset_y,
            self.hitbox_width,
            self.hitbox_height
        )

        # Check if solid
        self.solid = self.collision_type == "solid"

    def update(self, level):
        """Override in subclasses if needed"""
        pass