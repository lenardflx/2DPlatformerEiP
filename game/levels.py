import json
import os.path

import pygame
from core.game_data import get_game_data

class Level:
    def __init__(self, level_number):
        with open("assets/levels/levels.json") as f:
            loc = json.load(f)
            self.blueprint = pygame.image.load(os.path.join("assets/levels",loc[str(level_number)])).convert_alpha()
        self.scale: int = get_game_data("level_scale")
        self.tile_textures, self.collision_types = self.load_tiles()
        self.gravity = 3
        self.tiles = self.process_blueprint()

        self.height = len(self.tiles[0]) * self.scale
        self.width = len(self.tiles) * self.scale

    def load_tiles(self):
        with open("assets/tiles/textures.json") as f:
            loc = json.load(f)
        textures = {}
        collision_types = {}
        for color, path in loc.items():
            textures[color] = pygame.image.load(os.path.join("assets/tiles",path["texture"])).convert_alpha()
            collision_types[color] = path["collision_type"]
        return textures, collision_types

    def process_blueprint(self):
        w, h = self.blueprint.get_size()
        pixel_array = pygame.PixelArray(self.blueprint)

        tiles = []
        for x in range(w):
            row = []
            for y in range(h):
                color = self.blueprint.unmap_rgb(pixel_array[x, y])
                code = f"{color[0]},{color[1]},{color[2]}" if color[3] != 0 else None
                row.append(self.tile_textures.get(code, None))

            tiles.append(row)

        return tiles


    def render(self, screen):
        for x, row in enumerate(self.tiles):
            for y, tile in enumerate(row):
                if tile:
                    screen.blit(pygame.transform.scale(tile, (self.scale, self.scale)), (x * self.scale, y * self.scale))