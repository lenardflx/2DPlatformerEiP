import json
import pygame

from core.camera import Camera
from core.game_data import get_game_data
from game.background import Background
from game.levels import Level
from game.menu import Menu, MenuState
from core.controls import Controls
from game.user_interface import UI

class GameEngine:
    def __init__(self):
        pygame.init()

        # Load game settings
        self.native_size = get_game_data("screen_size")
        self.fps = get_game_data("fps")
        self.dt = 1 / self.fps
        self.controls = Controls()

        # Initialize screen
        self.screen = pygame.display.set_mode(self.native_size, pygame.RESIZABLE)
        pygame.display.set_caption(get_game_data("game_title"))
        self.scaled_surface = pygame.Surface(self.native_size)

        # Initialize game state
        self.clock = pygame.time.Clock()
        self.current_level = 0
        self.is_playing = False  # Starts in a menu

        # Load first level
        self.level = Level(self.current_level, self.controls)

        # Store all sprites in groups
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.all_sprites.add(self.level, self.level.player, *self.level.enemies)

        # Load background
        with open("assets/background/background.json") as f:
            data = json.load(f)
        self.backgrounds = [Background(d) for d in data[::-1]]

        # UI and Menu
        self.ui = UI()
        self.menu = Menu(self.native_size)
        self.menu.active_type = MenuState.START

        #Ability Cooldown
        self.cooldown = 0

        # Camera System
        self.camera = Camera(self.native_size[0], self.native_size[1], self.level.width, self.level.height)

    def start_game(self):
        """Starts or resumes gameplay."""
        self.is_playing = True
        self.menu.active_type = None  # No menu is active

    def load_next_level(self):
        """Loads the next level and resets the game state."""
        self.current_level += 1
        self.level = Level(self.current_level, self.controls)
        self.camera = Camera(self.native_size[0], self.native_size[1], self.level.width, self.level.height)

        self.all_sprites.empty()
        self.all_sprites.add(self.level, self.level.player, *self.level.enemies)

    def handle_events(self):
        """Handles all game events like input and window resizing."""
        for event in pygame.event.get():  # Process one event at a time
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if self.controls.is_action_active("gravity_inverse"):
                self.flip_gravity()

            if self.is_playing:
                # Game is running
                if self.controls.is_action_active("menu"):
                    self.menu.active_type = MenuState.PAUSE  # Open pause menu
                    self.is_playing = False  # Pause the game

                self.ui.handle_event(event, self)  # Pass single event to UI
            else:
                self.menu.handle_event(event, self)  # Pass single event to Menu

    def flip_gravity(self):
        
        """Flips gravity and mirrors entities vertically."""
        if self.cooldown > 0:
            return # Prevent flipping mid-air
        self.cooldown = 60

        self.level.gravity *= -1
        for entity in [self.level.player] + list(self.level.enemies):
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
        if self.cooldown > 0:
            self.cooldown -= 1
        """Updates all game objects and logic."""
        if self.is_playing:
            self.level.update(self.dt, self)

            self.camera.follow(self.level.player)
            self.ui.update(self.level.player)
            self.level.check_touch(self.level.player, self)

        if self.level.player.health <= 0:
            self.menu.active_type = MenuState.DEATH
            self.is_playing = False

    def run(self):
        """Main game loop."""
        while True:
            self.clock.tick(self.fps)
            self.handle_events()
            self.update()
            self.render()
