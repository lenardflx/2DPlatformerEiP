import pygame


class Entity:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        #hit gibt an ob mit etwas kollidiert wurde
        self.hit = False
    spikes = False

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
            if 0 <= x < len(level.tile_collisions) and 0 <= y_tile < len(level.tile_collisions[0]):
                if level.tile_collisions[x][y_tile] == "solid":
                    if self.velocity.y > 0:
                        self.rect.bottom = y_tile * level.scale
                        self.on_ground = True
                    else:
                        self.rect.top = (y_tile + 1) * level.scale
                    self.velocity.y = 0
                    return
                elif level.tile_collisions[x][y_tile] == "damage":
                    self.spikes = True
                    return
        self.on_ground = False

    def handle_horizontal_collisions(self, level):
        future_rect = self.rect.move(self.velocity.x, 0)
        x_tile = future_rect.right // level.scale if self.velocity.x > 0 else future_rect.left // level.scale
        y_top, y_bottom = (self.rect.top + 1) // level.scale, (self.rect.bottom - 1) // level.scale

        for y in range(y_top, y_bottom + 1):
            if 0 <= x_tile < len(level.tile_collisions) and 0 <= y < len(level.tile_collisions[0]):
                if level.tile_collisions[x_tile][y] == "solid":
                    if self.velocity.x > 0:
                        self.rect.right = x_tile * level.scale
                    else:
                        self.rect.left = (x_tile + 1) * level.scale
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
