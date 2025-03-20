import pygame
from game.tiles.tiles_register import register_tile


@register_tile("block")
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