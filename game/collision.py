def check_collision(entity,level, dx=0, dy=0):
    x_tile = int((entity.x + dx) / level.scale)
    y_tile = int((entity.y + dy) / level.scale)

    print(entity.x, entity.y, dx, dy, x_tile, y_tile)
    if x_tile <= 0:
        return "border left"
    if y_tile <= 0:
        return "border top"
    if x_tile >= len(level.tiles):
        return "border right"
    if y_tile >= len(level.tiles[0]):
        return "border bottom"

    key = level.tiles[y_tile][x_tile]
    return level.collision_types.get(key,"air")