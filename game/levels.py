import json
import pygame
import os

from core.game_data import get_game_data
from game.enemies.enemy_registry import ENEMY_CLASSES
from game.tiles.basic_tile import Tile
from game.tiles.tiles_register import TILES_CLASSES
from game.player import Player  # Import Player

class Level(pygame.sprite.LayeredUpdates):
    def __init__(self, level_number, controls):
        super().__init__()

        # Load tile metadata
        with open("assets/tiles/tiles.json") as f:
            self.tile_data = json.load(f)

        self.tile_size = self.tile_data["tile_size"]
        self.tile_set = pygame.image.load("assets/tiles/tile_set.png").convert_alpha()

        self.tiles = pygame.sprite.Group()
        self.updating_tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.spawn = (0, 0)
        self.player = None

        self.gravity = 9.8

        # Placeholder values for level size
        self.width = 0
        self.height = 0

        self.load_level(level_number, controls)

    def load_level(self, level_number, controls):
        """Loads level structure from assets/levels/level_<id>.json"""
        level_path = f"assets/levels/level_{level_number}.json"
        if not os.path.exists(level_path):
            raise FileNotFoundError(f"Level file {level_path} not found!")

        with open(level_path) as f:
            level_data = json.load(f)

        # Create player
        self.spawn = (level_data["spawn"][0] * self.tile_size, level_data["spawn"][1] * self.tile_size)
        w, h = get_game_data("player_size")
        s = get_game_data("player_scale")
        self.player = Player(self.spawn[0], self.spawn[1], w, h, s, controls)

        # Load enemies from JSON
        for enemy_data in level_data.get("enemies", []):
            enemy_type = enemy_data["type"]
            x, y = enemy_data["x"] * self.tile_size, enemy_data["y"] * self.tile_size
            print(enemy_type,ENEMY_CLASSES)
            if enemy_type in ENEMY_CLASSES:
                enemy = ENEMY_CLASSES[enemy_type](x, y, self.tile_size, self.tile_size, 1, self.player)
                self.enemies.add(enemy)

        # Load tiles
        for y, row in enumerate(level_data["tiles"]):
            for x, tile_id in enumerate(row):
                if tile_id == 0:
                    continue
                if str(tile_id) in self.tile_data["tiles"]:
                    tile_info = self.tile_data["tiles"][str(tile_id)]
                    tile_class = TILES_CLASSES.get(tile_info["type"], Tile)
                    tile = tile_class(x * self.tile_size, y * self.tile_size, tile_info, self.tile_set)

                    self.tiles.add(tile)
                    self.add(tile)

                    if tile.update_required:
                        self.updating_tiles.add(tile)

                self.width = max(self.width, (x + 1) * self.tile_size)
                self.height = max(self.height, (y + 1) * self.tile_size)

    def get_tile_at(self, x, y):
        """Returns the tile at the given position."""
        for tile in self.tiles:
            if tile.rect.collidepoint(x, y):
                return tile

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

    def update(self, dt, engine):
        """Updates tiles, enemies, and player."""
        self.updating_tiles.update(engine)

        for enemy in self.enemies:
            enemy.update(self, dt)

        self.player.update(self, dt)

    def render(self, screen, camera):
        """Renders everything inside the level."""
        for tile in self.tiles:
            screen.blit(tile.image, camera.apply(tile).topleft)
        for enemy in self.enemies:
            enemy.render(screen, camera)
        self.player.render(screen,camera)
