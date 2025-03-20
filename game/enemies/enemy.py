from game.enemies.enemy_registry import register_enemy
from game.entities import Entity

@register_enemy("basic_enemy")
class Enemy(Entity):
    def __init__(self, x, y, width, height, scale, player):
        super().__init__(x, y, width * scale, height * scale)
        self.player = player
        self.speed = 40
        self.jump_force = 160
        self.damage = 1
        self.attack_range = 30  # Attack range in pixels
        self.detection_range = 80  # Distance to start chasing the player

        # AI flags
        self.has_jumped = True
        self.drop = False
        self.obstacle = False
        self.hit = False

        # Load animations
        self.load_sprites("assets/characters/enemy.png",
                                         "assets/characters/enemy.json")

        self.state = "idle"
        self.sprite_index = 0
        self.image = self.sprites[self.state][self.sprite_index] if self.sprites.get(self.state) else None

    def update(self, level, dt):
        """Handles enemy movement and AI behavior."""
        # Chase player if nearby
        if abs(((self.rect.centerx-self.player.rect.centerx)**2 + (self.rect.centery-self.player.rect.centery)**2)**0.5) < self.detection_range:
            self.chase_player(dt)
        else:
            self.patrol(level, dt)

        if self.facing_right:
            self.drop       = not level.get_tile_at(self.rect.right + 1, self.rect.bottom + 1)
            self.obstacle   = (not level.get_tile_at(self.rect.right + 1, self.rect.bottom)) and level.get_tile_at(self.rect.right + 1, self.rect.bottom - 1)
        else:
            self.drop       = not level.get_tile_at(self.rect.left - 1, self.rect.bottom + 1)
            self.obstacle   = (not level.get_tile_at(self.rect.left - 1, self.rect.bottom)) and level.get_tile_at(self.rect.left - 1, self.rect.bottom - 1)

        if self.on_ground:
            self.has_jumped = False

        print(self.facing_right)

        # Jump over obstacles or gaps
        new_state = "jump"
        if self.drop and not self.has_jumped:
            self.jump(0.25 * self.speed, 2)
            self.has_jumped = True
        elif self.obstacle and not self.has_jumped:
            self.jump(0, 3)
            self.has_jumped = True
        else:
            new_state = "run"

        super().update(level, dt)
        self.state = new_state  # Update animation state

        # Attack player if touching them
        if self.rect.colliderect(self.player.rect):
            self.attack()

    def patrol(self, level, dt):
        """Moves the enemy left and right, reversing direction on collisions."""
        if self.facing_right:
            if self.rect.right >= level.width or self.hit:
                self.facing_right = False
            else:
                self.velocity.x = self.speed * dt
        else:
            if self.rect.left <= 0 or self.hit:
                self.facing_right = True
            else:
                self.velocity.x = -self.speed * dt

    def chase_player(self, dt):
        """Moves toward the player if within detection range."""
        if self.rect.centerx < self.player.rect.centerx:
            self.velocity.x = self.speed * dt
            self.facing_right = True
        else:
            self.velocity.x = -self.speed * dt
            self.facing_right = False

    def attack(self):
        """Handles enemy attacking logic."""
        self.player.got_hit = (self.damage, 60, 2)

    def jump(self, x_vel, y_vel):
        """Applies jump force to the enemy."""
        if self.facing_right:
            self.velocity.x = x_vel
        else:
            self.velocity.x = -x_vel
        
        self.velocity.y = -y_vel

    def eliminate(self):
        """Handles enemy elimination."""
        self.kill()
