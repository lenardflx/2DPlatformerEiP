import json
import os.path
import pygame
from core.game_data import get_game_data
from game.tiles import BLOCK_TYPES, Block

class Level:
    def __init__(self, level_number):
        with open("assets/levels/levels.json") as f:
            loc = json.load(f)
            self.blueprint = pygame.image.load(os.path.join("assets/levels",loc[str(level_number)])).convert_alpha()
        self.scale: int = get_game_data("level_scale")
        self.tiles_data = self.load_tiles()
        self.gravity = 9.81
        self.tiles, self.tile_collisions = self.process_blueprint()
        self.spawn = (100,100)

        self.height = len(self.tiles[0]) * self.scale
        self.width = len(self.tiles) * self.scale

    def load_tiles(self):
        with open("assets/tiles/tiles.json") as f:
            loc = json.load(f)

        tile_data = {}
        for color, path in loc.items():
            block_class = BLOCK_TYPES.get(path.get("type","block"), Block)
            tile_data[color] = block_class(path["texture"], path["collision_type"], path.get("metadata",{}))

        return tile_data

    def process_blueprint(self):
        w, h = self.blueprint.get_size()
        pixel_array = pygame.PixelArray(self.blueprint)
        tiles = []
        collisions = []

        for x in range(w):
            row_tiles = []
            row_collisions = []
            for y in range(h):
                color = self.blueprint.unmap_rgb(pixel_array[x, y])
                color_key = f"{color[0]},{color[1]},{color[2]}" if color[3] == 255 else None

                tile_class = self.tiles_data.get(color_key, None)
                row_tiles.append(tile_class)
                row_collisions.append(tile_class.collision_type if tile_class else "air")

            tiles.append(row_tiles)
            collisions.append(row_collisions)

        del pixel_array
        return tiles, collisions

    def check_touch(self, player, engine):
        if not player.on_ground:
            return
        tile_x = player.rect.centerx // self.scale
        tile_y = player.rect.centery // self.scale

        if 0 <= tile_x < len(self.tiles) and 0 <= tile_y < len(self.tiles[0]):
            block = self.tiles[tile_x][tile_y]
            if block and hasattr(block, "on_touch"):
                block.on_touch(engine)

    def render(self, screen, camera):
        cam_x, cam_y, cam_w, cam_h = camera.get_viewport()

        start_x = max(0, cam_x // self.scale)
        end_x = min(len(self.tiles), (cam_x + cam_w) // self.scale + 1)
        start_y = max(0, cam_y // self.scale)
        end_y = min(len(self.tiles[0]), (cam_y + cam_h) // self.scale + 1)

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                tile = self.tiles[x][y]
                if tile and camera.is_visible(x * self.scale, y * self.scale, self.scale, self.scale):
                    tile.render(screen, camera, x, y, self.scale)
