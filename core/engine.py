import json
import pygame

from core.camera import Camera
from core.game_data import get_game_data
from game.background import Background
from game.enemies.enemy_registry import ENEMY_CLASSES
from game.levels import Level
from game.menu import Menu, MenuOptions
from game.player import Player
from core.controls import Controls
from game.user_interface import UI

class GameEngine:
    def __init__(self):
        pygame.init()

        # Load game settings
        self.native_size = get_game_data("screen_size")
        self.fps = get_game_data("fps")
        self.controls = Controls()

        # Initialize screen
        self.screen = pygame.display.set_mode(self.native_size, pygame.RESIZABLE)
        pygame.display.set_caption(get_game_data("game_title"))
        self.scaled_surface = pygame.Surface(self.native_size)

        self.clock = pygame.time.Clock()
        self.current_level = 0
        self.is_playing = False  # Starts in a menu, not gameplay

        # Load level, player, and enemies dynamically
        self.level = Level(self.current_level)
        self.player = self.load_player()
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.enemies = []
        self.all_sprites.add(self.level, self.player, *self.enemies)
        self.load_enemies()

        # Load background
        with open("assets/background/background.json") as f:
            data = json.load(f)
        self.backgrounds = [Background(d) for d in data[::-1]]

        # UI and Menu
        self.ui = UI()
        self.menu = Menu()
        self.menu.active_type = MenuOptions.START

        # Camera System
        self.camera = Camera(self.native_size[0], self.native_size[1], self.level.width, self.level.height)

    def load_player(self):
        """Initialize player using level spawn point."""
        w, h = get_game_data("player_size")
        s = get_game_data("player_scale")
        x, y = self.level.spawn
        return Player(x, y, w, h, s, self.controls)

    def start_game(self):
        """Starts or resumes gameplay."""
        self.is_playing = True
        self.menu.active_type = None  # No menu is active

    def load_enemies(self):
        """Loads enemies from the current level data."""
        self.enemies = pygame.sprite.Group()

        for enemy_data in self.level.enemy_data:
            enemy_type = enemy_data["type"]
            x, y = enemy_data["x"], enemy_data["y"]

            if enemy_type in ENEMY_CLASSES:
                enemy = ENEMY_CLASSES[enemy_type](x, y, self.level.tile_size, self.level.tile_size, 1, self.player)
                self.enemies.add(enemy)

        self.all_sprites.empty()  # Clear old sprites
        self.all_sprites.add(self.level, self.player, *self.enemies)  # Add everything again

    def load_next_level(self):
        """Loads the next level and resets the game state."""
        self.current_level += 1
        self.level = Level(self.current_level)
        self.camera = Camera(self.native_size[0], self.native_size[1], self.level.width, self.level.height)
        self.player = self.load_player()

        self.level.load_enemies(self.level.get_enemies(), self.player)

        self.all_sprites.empty()
        self.all_sprites.add(self.level, self.player, *self.enemies)

    def handle_events(self):
        """Handles all game events like input and window resizing."""
        for event in pygame.event.get():  # Process one event at a time
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if self.controls.is_action_active("gravity_inverse"):
                    self.flip_gravity()

            if self.is_playing:
                # Game is running
                if self.controls.is_action_active("menu"):
                    self.menu.active_type = MenuOptions.PAUSE  # Open pause menu
                    self.is_playing = False  # Pause the game

                self.ui.handle_event(event, self)  # Pass single event to UI
            else:
                self.menu.handle_event(event, self)  # Pass single event to Menu

    def flip_gravity(self):
        """Flips gravity and mirrors entities vertically."""
        if not self.player.on_ground:
            return # Prevent flipping mid-air

        self.level.gravity *= -1
        for entity in [self.player] + list(self.enemies):
            entity.flip_gravity()

    def render(self):
        """Renders everything on a fixed surface and scales it while keeping the aspect ratio."""
        self.scaled_surface.fill((0, 0, 0))  # Clear the render surface

        if self.is_playing:
            # Render background
            for background in self.backgrounds:
                background.render(self.scaled_surface, self.camera)

            # Render game objects
            for sprite in self.all_sprites:
                pos = self.camera.apply(sprite).topleft
                self.scaled_surface.blit(sprite.image, pos)

            # Draw UI separately (not affected by camera)
            self.ui.render(self.scaled_surface)

        else:
            # Render menu if not playing
            self.menu.render(self.scaled_surface)

        # Scale and center final image
        self.scale_and_center()
        pygame.display.flip()

    def scale_and_center(self):
        """Scales the render surface while maintaining aspect ratio and adds black bars."""
        window_width, window_height = self.screen.get_size()
        scale = min(window_width / self.native_size[0], window_height / self.native_size[1])

        new_width = int(self.native_size[0] * scale)
        new_height = int(self.native_size[1] * scale)
        scaled_surface = pygame.transform.scale(self.scaled_surface, (new_width, new_height))

        x_offset = (window_width - new_width) // 2
        y_offset = (window_height - new_height) // 2

        self.screen.fill((0, 0, 0))  # Black bars
        self.screen.blit(scaled_surface, (x_offset, y_offset))

    def update(self):
        """Updates all game objects and logic."""
        if self.is_playing:
            dt = 1 / self.fps  # Get delta time
            self.player.update(self.level, dt)

            for enemy in self.enemies:
                enemy.update(self.level, dt)

            self.camera.follow(self.player)
            self.ui.update(self.player)
            self.level.check_touch(self.player, self)

            # Update all updating tiles separately
            self.level.updating_tiles.update(self)

        if self.player.health <= 0:  # Player died
            self.menu.active_type = MenuOptions.DEATH
            self.is_playing = False

    def run(self):
        """Main game loop."""
        while True:
            self.clock.tick(self.fps)
            self.handle_events()
            self.update()
            self.render()
