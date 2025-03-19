import os.path
import pygame

BLOCK_TYPES = {}

def register_block(block_type):
    def wrapper(cls):
        BLOCK_TYPES[block_type] = cls
        return cls
    return wrapper

@register_block("block")
class Block:
    def __init__(self, texture, collision_type, metadata=None):
        self.texture = pygame.image.load(os.path.join("assets/tiles", texture)).convert_alpha()
        self.collision_type = collision_type
        self.metadata = metadata or {}
        self.special_render = True

        self.hitbox_width = self.metadata.get("hitbox_width", 1.0)
        self.hitbox_height = self.metadata.get("hitbox_height", 1.0)
        self.hitbox_offset_x = self.metadata.get("hitbox_offset_x", 0.0)
        self.hitbox_offset_y = self.metadata.get("hitbox_offset_y", 0.0)

    def get_hitbox(self, x, y, scale):
        return pygame.Rect(
            x + self.hitbox_offset_x * scale,
            y + self.hitbox_offset_y * scale,
            self.hitbox_width * scale,
            self.hitbox_height * scale
        )

    def render(self, screen, camera, x, y, scale):
        tile_rect = pygame.Rect(x * scale, y * scale, scale, scale)
        screen.blit(pygame.transform.scale(self.texture, (scale, scale)), camera.apply(tile_rect))

@register_block("pressure_plate")
class PressurePlate(Block):
    def on_touch(self, engine):
        engine.load_next_level()


@register_block("moving_platform")
class MovingPlatform(Block):
    def __init__(self, texture, collision_type, metadata=None):
        super().__init__(texture, collision_type, metadata or {})

        self.special_render = True  # Damit Level.render() sie berücksichtigt
        self.speed = self.metadata.get("speed", 1)
        self.direction = self.metadata.get("direction", "horizontal")
        self.movement_direction = 1

    def update(self, level, dt):
        for x in range(len(level.tiles)):
            for y in range(len(level.tiles[x])):
                if level.tiles[x][y] == self:
                    movement = pygame.Vector2(self.speed * self.movement_direction * dt,
                                              0) if self.direction == "horizontal" else pygame.Vector2(0,
                                                                                                       self.speed * self.movement_direction * dt)

                    new_x, new_y = x + movement.x / level.scale, y + movement.y / level.scale
                    new_x, new_y = int(new_x), int(new_y)

                    if 0 <= new_x < len(level.tiles) and 0 <= new_y < len(level.tiles[0]):
                        if level.tiles[new_x][new_y] is None or level.tiles[new_x][new_y].collision_type != "solid":
                            level.tiles[x][y] = None
                            level.tiles[new_x][new_y] = self
                        else:
                            self.movement_direction *= -1
                    else:
                        self.movement_direction *= -1
                    return

    def render(self, screen, camera, x, y, scale):
        tile_rect = pygame.Rect(x * scale, y * scale, self.hitbox_width * scale, self.hitbox_height * scale)
        screen.blit(
            pygame.transform.scale(self.texture, (int(self.hitbox_width * scale), int(self.hitbox_height * scale))),
            camera.apply(tile_rect))
