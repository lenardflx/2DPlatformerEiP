from game.tiles.basic_tile import Tile
from game.tiles.tiles_register import register_tile

@register_tile("spike")
class Spikes(Tile):
    def __init__(self, x, y, tile_info, tile_set, tile_size):
        super().__init__(x, y, tile_info, tile_set, tile_size)

        self.damage = self.metadata.get("damage", 1)
        self.update_required = True

    def update(self, engine):
        """Check for collisions with entities and deal damage."""
        for entity in [engine.level.player] + list(engine.level.enemies):
            if self.rect.colliderect(entity.rect):  # If entity touches spikes
                entity.hit(self)  # Call the hit function
