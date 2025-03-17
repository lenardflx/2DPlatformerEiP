import json

with open("assets/tiles/collision_priority.json") as f:
    COLLISION_PRIORITY = json.load(f)

def get_highest_priority(keys, level):
    highest_priority = "air"
    max_priority_value = COLLISION_PRIORITY[highest_priority]

    print(keys)

    return highest_priority

def check_collision(entity, level, dx=0, dy=0):
    x_tile_left = int((entity.x + dx) / level.scale)
    x_tile_right = int((entity.x + entity.width + dx - 1) / level.scale)
    y_tile_top = int((entity.y + dy) / level.scale)
    y_tile_bottom = int((entity.y + entity.height + dy - 1) / level.scale)

    if x_tile_left < 0 or x_tile_right >= len(level.tiles):
        return "solid"
    if y_tile_top < 0:
        return "ceiling"
    if y_tile_bottom >= len(level.tiles[0]):
        return "floor"

    keys = [
        level.tiles[y_tile_top][x_tile_left],  # Oben links
        level.tiles[y_tile_top][x_tile_right], # Oben rechts
        level.tiles[y_tile_bottom][x_tile_left], # Unten links
        level.tiles[y_tile_bottom][x_tile_right] # Unten rechts
    ]

    return get_highest_priority(keys, level)
