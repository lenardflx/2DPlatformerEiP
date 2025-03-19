import pygame


class Entity:
    def __init__(self, x, y, width, height):
        self.spikes = False
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.hit = False

    def update(self, level, dt):
        self.hit = False
        self.velocity.y += level.gravity * dt
        self.move(level)

    def move(self, level):
        self.rect.x += self.velocity.x
        self.handle_horizontal_collisions(level)

        self.on_ground = False
        self.rect.y += self.velocity.y
        self.handle_vertical_collisions(level)

    def handle_vertical_collisions(self, level):
        future_rect = self.rect.move(0, self.velocity.y)
        x_left, x_right = self.rect.left // level.scale, (self.rect.right - 1) // level.scale
        y_tile = future_rect.bottom // level.scale if self.velocity.y > 0 else future_rect.top // level.scale

        for x in range(x_left, x_right + 1):
            if 0 <= x < len(level.tiles) and 0 <= y_tile < len(level.tiles[0]):
                block = level.tiles[x][y_tile]
                if block:
                    block_hitbox = block.get_hitbox(x * level.scale, y_tile * level.scale, level.scale)

                    if block.collision_type == "solid":
                        if self.velocity.y > 0 and future_rect.colliderect(block_hitbox):
                            self.rect.bottom = block_hitbox.top
                            self.velocity.y = 0
                            self.on_ground = True
                            return
                        elif self.velocity.y < 0 and future_rect.colliderect(block_hitbox):
                            self.rect.top = block_hitbox.bottom
                            self.velocity.y = 0
                            return

                    elif block.collision_type == "moving_platform" and self.velocity.y > 0:
                        if self.rect.bottom <= block_hitbox.top <= future_rect.bottom:
                            self.rect.bottom = block_hitbox.top
                            self.velocity.y = 0
                            self.on_ground = True
                            return
                    elif block.collision_type == "damage":
                        self.spikes = True
                        return
        self.on_ground = False

    def handle_horizontal_collisions(self, level):
        future_rect = self.rect.move(self.velocity.x, 0)
        x_tile = future_rect.right // level.scale if self.velocity.x > 0 else future_rect.left // level.scale
        y_top, y_bottom = (self.rect.top + 1) // level.scale, (self.rect.bottom - 1) // level.scale

        for y in range(y_top, y_bottom + 1):
            if 0 <= x_tile < len(level.tiles) and 0 <= y < len(level.tiles[0]):
                block = level.tiles[x_tile][y]
                if block:
                    block_hitbox = block.get_hitbox(x_tile * level.scale, y * level.scale, level.scale)

                    if block.collision_type == "solid":
                        if self.velocity.x > 0 and future_rect.colliderect(block_hitbox):
                            self.rect.right = block_hitbox.left
                            self.velocity.x = 0
                            self.hit = True
                            return
                        elif self.velocity.x < 0 and future_rect.colliderect(block_hitbox):
                            self.rect.left = block_hitbox.right
                            self.velocity.x = 0
                            self.hit = True
                            return

    def eliminate(self):
        print("eliminated")

    def render(self, screen, camera):
        sprite = self.sprites[self.state][self.sprite_index]

        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)

        screen.blit(sprite, camera.apply(self))
