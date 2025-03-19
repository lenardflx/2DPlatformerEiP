import json
import pygame
import os
from game.tiles import TILE_CLASSES, Tile
from game.enemies.enemy_registry import ENEMY_CLASSES

class Level(pygame.sprite.LayeredUpdates):
    def __init__(self, level_number):
        super().__init__()

        # Load tile metadata
        with open("assets/tiles/tiles.json") as f:
            self.tile_data = json.load(f)

        self.tile_size = self.tile_data["tile_size"]  # Get tile size
        self.tile_set = pygame.image.load("assets/tiles/tile_set.png").convert_alpha()

        self.tiles = pygame.sprite.Group()
        self.updating_tiles = pygame.sprite.Group()  # Holds all tiles that require updates
        self.enemy_data = []
        self.spawn = (0, 0)

        self.gravity = 9.8

        # Initialize level size (FIXED)
        self.width = 0
        self.height = 0

        self.load_level(level_number)

    def load_level(self, level_number):
        """Loads level structure from assets/levels/level_<id>.json"""
        level_path = f"assets/levels/level_{level_number}.json"
        if not os.path.exists(level_path):
            raise FileNotFoundError(f"Level file {level_path} not found!")

        with open(level_path) as f:
            level_data = json.load(f)

        # Convert spawn position from tile units to pixels
        self.spawn = (level_data["spawn"][0] * self.tile_size, level_data["spawn"][1] * self.tile_size)

        # Store raw enemy data
        self.enemy_data = level_data.get("enemies", [])

        # Load tiles and calculate level width/height (FIXED)
        for y, row in enumerate(level_data["tiles"]):
            for x, tile_id in enumerate(row):
                if tile_id == 0:  # Ignore Tile ID 0 (empty space)
                    continue
                if str(tile_id) in self.tile_data["tiles"]:
                    tile_info = self.tile_data["tiles"][str(tile_id)]
                    tile_class = TILE_CLASSES.get(tile_info["type"], Tile)  # Select correct class
                    tile = tile_class(x * self.tile_size, y * self.tile_size, tile_info, self.tile_set)

                    self.tiles.add(tile)
                    self.add(tile)

                    # Add updating tiles
                    if tile.update_required:
                        self.updating_tiles.add(tile)

                # Track the level width & height dynamically
                self.width = max(self.width, (x + 1) * self.tile_size)
                self.height = max(self.height, (y + 1) * self.tile_size)

    def get_solid_tiles_near(self, entity, radius=2):
        """Returns a list of solid tiles near the given entity for collision checking."""
        nearby_tiles = []
        ex, ey = entity.rect.center  # Get entity position
        tile_x, tile_y = ex // self.tile_size, ey // self.tile_size  # Convert to tile coordinates

        for y in range(tile_y - radius, tile_y + radius + 1):
            for x in range(tile_x - radius, tile_x + radius + 1):
                if 0 <= x < (self.width // self.tile_size) and 0 <= y < (self.height // self.tile_size):
                    for tile in self.tiles:
                        if tile.rect.colliderect(
                                pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)):
                            if getattr(tile, "solid", False):  # Ensure the tile is solid
                                nearby_tiles.append(tile)

        return nearby_tiles

    def check_touch(self, entity, engine):
        """Checks if the entity is touching an interactive tile (e.g., exits, pressure plates)."""
        for tile in self.get_solid_tiles_near(entity):
            if hasattr(tile, "on_touch"):  # If the tile has a special interaction
                tile.on_touch(engine)  # Trigger the tile's interaction

    def check_collision(self, entity):
        """Checks for collision with solid tiles."""
        return pygame.sprite.spritecollide(entity, self.tiles, False, lambda e, t: t.solid)

    def update(self):
        """Updates only tiles that require updating"""
        self.updating_tiles.update()

    def render(self, screen, camera):
        """Renders the level tiles within camera view."""
        self.tiles.draw(screen)
