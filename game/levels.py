import json
import pygame
import os
import math

from core.game_data import get_game_data
from game.enemies.enemy_registry import ENEMY_CLASSES
from game.tiles.basic_tile import Tile
from game.tiles.tiles_register import TILES_CLASSES
from game.player import Player  # Import Player

class Level(pygame.sprite.LayeredUpdates):
    def __init__(self, level_number, controls, sound_manager):
        super().__init__()

        # Load tile metadata
        with open(f"assets/tiles/level_{level_number}_data.json") as f:
            self.tile_data = json.load(f)

        self.tile_size = self.tile_data["tile_size"]
        self.tile_set = pygame.image.load(f"assets/tiles/level_{level_number}_set.png").convert_alpha()

        self.tile_grid = []  # 2D array for fast solid tile lookup
        self.grid_width = 0
        self.grid_height = 0
        self.mp = []
        self.c = 0

        self.tiles = pygame.sprite.Group()
        self.updating_tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.spawn = (0, 0)
        self.player = None

        self.gravity = 12

        # Placeholder values for level sizaae
        self.width = 0
        self.height = 0

        self.sound_manager = sound_manager
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
        self.player = Player(
            self.spawn[0], self.spawn[1],
            "assets/characters/player.png",
            "assets/characters/player.json",
            controls, self, self.sound_manager
        )

        # Load enemies from JSON
        for enemy_data in level_data.get("enemies", []):
            enemy_type = enemy_data["type"]
            x, y = enemy_data["x"] * self.tile_size, enemy_data["y"] * self.tile_size
            if enemy_type in ENEMY_CLASSES:
                enemy = ENEMY_CLASSES[enemy_type](
                    x, y,
                    f"assets/characters/{enemy_type}.png",
                    f"assets/characters/{enemy_type}.json",
                    self.player, self, self.sound_manager
                )
                self.enemies.add(enemy)

        # Load tiles from JSON
        tile_map = level_data["tiles"]
        self.grid_height = len(tile_map)
        self.grid_width = max(len(row) for row in tile_map)
        self.tile_grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        for y, row in enumerate(tile_map):
            for x, tile_id in enumerate(row):
                if tile_id == 0:
                    continue

                tile_info = self.tile_data["tiles"].get(str(tile_id))
                if not tile_info:
                    continue

                tile_class = TILES_CLASSES.get(tile_info["type"], Tile)
                tile = tile_class(x * self.tile_size, y * self.tile_size, tile_info, self.tile_set, self.tile_size)

                self.tiles.add(tile)
                self.add(tile)

                if tile.update_required:
                    self.updating_tiles.add(tile)
                if tile.solid:
                    self.tile_grid[y][x] = tile

                self.width = max(self.width, (x + 1) * self.tile_size)
                self.height = max(self.height, (y + 1) * self.tile_size)

        # Rebuild the pathfinding grid
        for enemy in self.enemies:
            if hasattr(enemy, "set_level"):
                enemy.set_level(self)

    def get_tile_at(self, x, y):
        """Returns the tile at the given world coordinate in pixel (x, y)."""
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return self.tile_grid[grid_y][grid_x]
        return None

    def get_solid_tiles_near(self, entity, radius=2):
        """Returns nearby solid tiles for physics checks (grid + dynamic)."""
        nearby_tiles = []
        ex, ey = entity.rect.center
        tile_x, tile_y = int(ex // self.tile_size), int(ey // self.tile_size)

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                gx = tile_x + dx
                gy = tile_y + dy
                if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
                    tile = self.tile_grid[gy][gx]
                    if tile:
                        nearby_tiles.append(tile)

        # Also check moving / dynamic tiles
        for tile in self.updating_tiles:
            if getattr(tile, "solid", False) and entity.rect.colliderect(tile.rect):
                nearby_tiles.append(tile)

        return nearby_tiles

    def flip_gravity(self):
        """Flips gravity and mirrors entities vertically."""
        self.gravity *= -1
        for entity in [self.player] + list(self.enemies):
            entity.flip_gravity()

    def check_touch(self, entity, engine):
        """Checks if the entity is touching an interactive tile (e.g., exits, pressure plates)."""
        for tile in self.get_solid_tiles_near(entity):
            if hasattr(tile, "on_touch"):  # If the tile has a special interaction
                tile.on_touch(engine)  # Trigger the tile's interaction

    def check_collision(self, entity):
        return any(tile.rect.colliderect(entity.rect) for tile in self.get_solid_tiles_near(entity))

    def get_closest_pos(self, entity):
        """Returns the closest position to entity."""
        ex, ey = entity.rect.center
        tile_x, tile_y = int(ex // self.tile_size), int(ey // self.tile_size)

        return tile_x, tile_y
    def distance_to(self, entity,grid_range=5):
        with open(f"assets/levels/level_0.json") as f:
            level_data = json.load(f)
        pos=self.get_closest_pos(entity)
        grid = level_data["tiles"]
        for x in range(-grid_range, grid_range):
            for y in range(-grid_range, grid_range):
                if getattr(self.tile_grid[pos[0]+x][pos[1]+y], "solid", False):
                    grid[pos[0]+x][pos[1]+y]=100+abs(x)+abs(y)
                else:
                    grid[pos[0]+x][pos[1]+y]=-1
        print(grid)

    def update(self, dt, engine):
        """Updates tiles, enemies, and player."""
        if self.c % 30 == 0:
            self.c = 0
            self.setup_player_map(self.player.rect.centerx, self.player.rect.centery)

        self.c += 1

        self.updating_tiles.update(engine)

        for enemy in self.enemies:
            enemy.update(self, dt)

        self.player.update(self, dt)
        #self.distance_to(self.player)

    def render(self, screen, camera):
        """Renders everything inside the level."""
        for tile in self.tiles:
            screen.blit(tile.image, camera.apply(tile).topleft)
        for enemy in self.enemies:
            enemy.render(screen, camera)
        self.player.render(screen,camera)
        
        #score_font = pygame.font.Font(None, 20)
        #for x, row in enumerate(self.mp):
        #    for y, col in enumerate(row):
        #        x_new = self.tile_size * x
        #        y_new = self.tile_size * y
        #        score_surf = score_font.render(str(col), False, (0, 0, 0))
        #        score_pos = [x_new, y_new]
        #        screen.blit(score_surf, score_pos)

    def setup_player_map(self, x, y):
        self.mp = [[1000 for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        for i in range(0, 10):
            self.create_player_map(0, x, y, i)

    def create_player_map(self, index, x, y, max):
        if index == max:
            return
        
        x_low = math.floor(x / self.tile_size)
        y_low = math.floor(y / self.tile_size)

        if (x_low < 0 or y_low < 0 or x_low >= self.grid_width or y_low >= self.grid_height):
           return
        if self.tile_grid[y_low][x_low]:
            return
        
        if self.mp[x_low][y_low] == 1000:
            self.mp[x_low][y_low] = index

        for c in [[-1, 0], [0, -1], [1, 0], [0, 1]]:
            x_new = x_low + c[0]
            y_new = y_low + c[1]
            self.create_player_map(index + 1, self.tile_size * x_new, self.tile_size * y_new, max)

