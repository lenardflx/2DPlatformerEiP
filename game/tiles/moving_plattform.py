import pygame
from game.tiles.basic_tile import Tile
from game.tiles.tiles_register import register_tile

@register_tile("moving_platform")
class MovingPlatform(Tile):
    def __init__(self, x, y, tile_info, tile_set, tile_size):
        super().__init__(x, y, tile_info, tile_set, tile_size)

        self.update_required = True  # Ensure the platform updates every frame

        self.speed = self.metadata.get("speed", 1)
        self.direction = self.metadata.get("direction", "horizontal")
        self.movement_direction = 1  # 1 = forward, -1 = reverse
        self.tile_size = tile_size  # Tile size reference for movement

        self.solid = True

    def update(self, engine):
        """Moves the platform and interacts with the player + enemies."""
        level = engine.level
        player = level.player
        next_x, next_y = self.rect.x, self.rect.y

        if self.direction == "horizontal":
            next_x += self.speed * self.movement_direction
            check_rect = pygame.Rect(
                next_x + (self.rect.width if self.movement_direction > 0 else -1),
                self.rect.y, 1, self.rect.height
            )  # Only check in movement direction (left/right)
        else:
            next_y += self.speed * self.movement_direction
            check_rect = pygame.Rect(
                self.rect.x,
                next_y + (self.rect.height if self.movement_direction > 0 else -1),
                self.rect.width, 1
            )  # Only check in movement direction (up/down)

        # Check for solid collisions
        if any(tile.rect.colliderect(check_rect) for tile in level.get_solid_tiles_near(self)):
            self.movement_direction *= -1  # Reverse direction
            return

        # Move platform if no collision
        delta_x = next_x - self.rect.x
        delta_y = next_y - self.rect.y
        self.rect.x, self.rect.y = next_x, next_y

        # Carry entities smoothly
        for entity in [player] + list(level.enemies):  # Convert Group to List
            if self.is_stuck_between_walls(entity, level):
                entity.eliminate()  # Kill stuck entity
                continue

            standing_on = (
                not entity.is_flipped and
                entity.rect.bottom == self.rect.top and  # Standing on platform
                entity.velocity.y >= 0 and  # Not jumping
                entity.rect.right > self.rect.left and entity.rect.left < self.rect.right  # Within platform bounds
            )

            hanging_under = (
                entity.is_flipped and
                entity.rect.top == self.rect.bottom and  # Hanging under platform
                entity.velocity.y <= 0 and  # Not jumping upwards
                entity.rect.right > self.rect.left and entity.rect.left < self.rect.right  # Within platform bounds
            )

            if standing_on or hanging_under:
                entity.rect.y += delta_y  # Move up/down with platform
                entity.rect.x += delta_x  # Stick horizontally
                entity.velocity.x = delta_x  # Sync velocity for smooth movement
                entity.on_ground = True

            # Push entities left or right if colliding from the sides
            elif self.colliding_from_side(entity, delta_x):
                entity.rect.x += delta_x  # Apply horizontal push
                if entity.on_ground:  # Prevent jumping issue
                    entity.velocity.x = delta_x

    @staticmethod
    def is_stuck_between_walls(entity, level):
        """Detects if an entity is stuck between a wall and a moving platform."""
        left_blocked = any(
            tile.rect.colliderect(pygame.Rect(entity.rect.left - 1, entity.rect.y, 1, entity.rect.height))
            for tile in level.get_solid_tiles_near(entity)
        )
        right_blocked = any(
            tile.rect.colliderect(pygame.Rect(entity.rect.right + 1, entity.rect.y, 1, entity.rect.height))
            for tile in level.get_solid_tiles_near(entity)
        )

        return left_blocked and right_blocked

    def colliding_from_side(self, entity, delta_x):
        """Check if entity is colliding with the platform from the side."""
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

        return (colliding_right or colliding_left) and entity.velocity.y >= 0  # No pushing while jumping