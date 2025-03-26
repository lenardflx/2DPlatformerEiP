import pygame
from game.tiles.basic_tile import Tile
from game.tiles.tiles_register import register_tile

@register_tile("moving_platform")
class MovingPlatform(Tile):
    def __init__(self, x, y, tile_info, tile_set, tile_size):
        super().__init__(x, y, tile_info, tile_set, tile_size)

        self.update_required = True  # Ensure the platform updates every frame

        self.speed = self.metadata.get("speed", 1)
        self.range = self.metadata.get("range", float('inf'))
        self.direction = self.metadata.get("direction", "horizontal")
        self.movement_direction = self.metadata.get("movement_direction", 1)  # 1 = forward, -1 = reverse
        self.tile_size = tile_size  # Tile size reference for movement
        self.distance = 0

        self.solid = True

    def update(self, engine):
        """Moves the platform and interacts with the player + enemies."""
        level = engine.level
        player = level.player

        self.distance += 1
        if self.distance >= self.range:
            self.distance = 0
            self.movement_direction *= -1

        if self.direction == "horizontal":
            delta_x = self.speed * self.movement_direction
            delta_y = 0
            next_rect = self.rect.move(delta_x, 0)
            check_rect = pygame.Rect(
                next_rect.right if self.movement_direction > 0 else next_rect.left - 1,
                next_rect.y, 1, next_rect.height
            )
        else:
            delta_x = 0
            delta_y = self.speed * self.movement_direction
            next_rect = self.rect.move(0, delta_y)
            check_rect = pygame.Rect(
                next_rect.x,
                next_rect.bottom if self.movement_direction > 0 else next_rect.top - 1,
                next_rect.width, 1
            )

        # Check for solid collisions
        if any(tile.rect.colliderect(check_rect) for tile in level.get_solid_tiles_near(self)):
            self.movement_direction *= -1
            return

        # Move platform if no collision
        self.rect = next_rect

        # Carry entities smoothly
        for entity in [player] + list(level.enemies):
            if type(entity).__name__ == "Neuros":
                continue
            is_above = (
                    not entity.is_flipped and
                    entity.rect.bottom == self.rect.top and
                    entity.velocity.y >= 0 and
                    self.rect.left < entity.rect.right and self.rect.right > entity.rect.left
            )

            is_below = (
                    entity.is_flipped and
                    entity.rect.top == self.rect.bottom and
                    entity.velocity.y <= 0 and
                    self.rect.left < entity.rect.right and self.rect.right > entity.rect.left
            )

            will_touch_wall = False
            if self.direction == "horizontal":
                future_rect = entity.rect.move(delta_x, 0)
                if delta_x != 0:
                    wall_check = pygame.Rect(future_rect.x, future_rect.y, future_rect.width, future_rect.height)
                    if any(tile.rect.colliderect(wall_check) for tile in level.get_solid_tiles_near(entity)):
                        will_touch_wall = True
            else:
                future_rect = entity.rect.move(0, delta_y)
                if delta_y != 0:
                    wall_check = pygame.Rect(future_rect.x, future_rect.y, future_rect.width, future_rect.height)
                    if any(tile.rect.colliderect(wall_check) for tile in level.get_solid_tiles_near(entity)):
                        will_touch_wall = True

            if self.direction == "horizontal:":
                # Carrying logic
                if (is_above or is_below) and not will_touch_wall:
                    entity.rect.y += delta_y
                    entity.rect.x += delta_x
                    entity.velocity.x = delta_x
                    entity.on_ground = True
                    continue
            else:
                # Carrying logic
                if (is_above or is_below) and not will_touch_wall:
                    entity.rect.y += delta_y
                    entity.rect.x += delta_x
                    entity.velocity.y = delta_y
                    entity.on_ground = True
                    continue

            # Check for wall collisions
            if self.colliding_from_side(entity, delta_x, delta_y):
                if self.is_stuck_between_walls(entity, level, self.direction):
                    entity.eliminate()
                elif self.direction == "horizontal":
                    entity.rect.x += delta_x
                    if entity.on_ground:
                        entity.velocity.x = delta_x
                else:
                    entity.rect.y += delta_y
                    if entity.on_ground:
                        entity.velocity.y = delta_y

    @staticmethod
    def is_stuck_between_walls(entity, level, direction):
        """Detects if an entity is stuck between a wall and a moving platform."""
        top_blocked = False
        bottom_blocked = False
        left_blocked = False
        right_blocked = False

        if direction == "horizontal":
            left_blocked = any(
                tile.rect.colliderect(pygame.Rect(entity.rect.left - 1, entity.rect.y, 1, entity.rect.height))
                for tile in level.get_solid_tiles_near(entity)
            )
            right_blocked = any(
                tile.rect.colliderect(pygame.Rect(entity.rect.right + 1, entity.rect.y, 1, entity.rect.height))
                for tile in level.get_solid_tiles_near(entity)
            )
        else:
            top_blocked = any(
                tile.rect.colliderect(pygame.Rect(entity.rect.x, entity.rect.top - 1, entity.rect.width, 1))
                for tile in level.get_solid_tiles_near(entity)
            )
            bottom_blocked = any(
                tile.rect.colliderect(pygame.Rect(entity.rect.x, entity.rect.bottom + 1, entity.rect.width, 1))
                for tile in level.get_solid_tiles_near(entity)
            )

        return (left_blocked and right_blocked) or (top_blocked and bottom_blocked)

    def colliding_from_side(self, entity, delta_x, delta_y):
        """Check if entity is colliding with the platform from the side."""
        colliding_right = False
        colliding_left = False
        colliding_top = False
        colliding_bottom = False

        if self.direction == "horizontal":
            colliding_right = (
                self.movement_direction > 0 and
                entity.rect.left < self.rect.right <= entity.rect.left + abs(delta_x) and
                entity.rect.bottom > self.rect.top and entity.rect.top < self.rect.bottom
            )
            colliding_left = (
                self.movement_direction < 0 and
                entity.rect.right > self.rect.left >= entity.rect.right - abs(delta_x) and
                entity.rect.bottom > self.rect.top and entity.rect.top < self.rect.bottom
            )
        else:
            colliding_bottom = (
                self.movement_direction > 0 and
                entity.rect.top < self.rect.bottom <= entity.rect.top + abs(delta_y) and
                (entity.rect.left < self.rect.right and entity.rect.right > self.rect.left)
            )
            colliding_top = (
                self.movement_direction < 0 and
                entity.rect.bottom > self.rect.top >= entity.rect.bottom - abs(delta_y) and
                (entity.rect.left < self.rect.right and entity.rect.right > self.rect.left)
            )

        rtn = (entity.velocity.y >= 0 and( 
            colliding_right or colliding_left or 
            colliding_top or colliding_bottom))

        return rtn # No pushing while jumping