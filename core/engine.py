import json
import pygame

from core.camera import Camera
from core.font import FontManager
from core.game_data import get_game_data
from core.sound import SoundManager
from game.background import Background
from game.levels import Level
from game.menu.menu import Menu, MenuState
from core.controls import Controls
from game.user_interface import UI

class GameEngine:
    def __init__(self):
        pygame.init()

        # Settings
        self.native_size = get_game_data("screen_size")
        self.fps = get_game_data("fps")
        self.dt = 1 / self.fps
        self.clock = pygame.time.Clock()
        self.controls = Controls()

        # Display
        self.screen = pygame.display.set_mode(self.native_size, pygame.RESIZABLE)
        pygame.display.set_caption(get_game_data("game_title"))
        self.scaled_surface = pygame.Surface(self.native_size)

        # Main Theme Music
        self.sound_manager = SoundManager()
        self.sound_manager.play_music()

        # Game State
        self.is_playing = False
        self.level = None
        self.current_level = None
        self.completed_levels = []

        # Pre-Level Slides
        self.story_texts = []
        self.story_index = 0
        self.tutorial_images = []
        self.tutorial_index = 0
        self.slide_mode = None
        self.slide_timer = 0
        self.slide_fade_duration = 30
        self.slide_display_duration = 180

        # Title Fade
        self.show_level_title = False
        self.level_title = ""
        self.level_title_timer = 0
        self.level_title_duration = 180
        self.level_title_fade = 30

        # Load Level Meta
        self.levels_data = {}
        self.level_count = 0
        self.load_level_metadata()

        # Core Components
        self.font_manager = FontManager(self.native_size)
        self.menu = Menu(self.native_size, self.controls, self.levels_data, self.font_manager, self.sound_manager)
        self.menu.active_type = MenuState.MAIN
        self.ui = UI()

        # Back-/Foregrounds (init later on level load)
        self.backgrounds = []
        self.foreground = None

        # Camera (init later on level load)
        self.camera = None

    def load_level_metadata(self):
        """Loads level metadata from assets/levels/levels.json."""
        with open("assets/levels/levels.json") as f:
            self.levels_data = json.load(f)
        self.level_count = len(self.levels_data)

    @property
    def next_level(self):
        """Returns the next level ID based on the last completed level."""
        if not self.completed_levels:
            return 0
        return (self.completed_levels[-1] + 1) % self.level_count

    def start_game(self):
        """Starts the game from the first level."""
        self.is_playing = True
        self.menu.active_type = MenuState.NONE
        self.load_levels_data(self.next_level)

    def load_levels_data(self, level_id):
        """Load story + tutorial slides before a level"""
        self.current_level = level_id
        level_data = self.levels_data.get(str(level_id), {})

        self.story_texts = level_data.get("story", [])
        self.story_index = 0
        self.tutorial_images = [pygame.image.load(path).convert_alpha() for path in level_data.get("tutorial", [])]
        self.tutorial_index = 0

        self.slide_mode = "story" if self.story_texts else "tutorial"

        bg_data = self.levels_data.get(str(level_id), {}).get("background", [])
        self.backgrounds = [Background(layer) for layer in bg_data[::-1]]
        self.foreground = pygame.image.load(level_data.get("foreground", "")).convert_alpha()
        self.foreground.set_alpha(75)

    def load_level(self, level_id):
        """Loads a level by ID."""
        self.level = Level(level_id, self.controls, self.sound_manager, self)
        self.camera = Camera(self.native_size[0], self.native_size[1], self.level.width, self.level.height)
        self.show_level_title = True
        self.level_title_timer = 0
        self.level_title = self.levels_data.get(str(level_id), {}).get("title", f"Level {level_id + 1}")

    def handle_events(self):
        """Handles all game events like input and window resizing."""
        for event in pygame.event.get():  # Process one event at a time
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if self.controls.is_action_active("menu"):
                if not self.menu.back_redirect == MenuState.MAIN:
                    self.menu.toggle_menu(MenuState.PAUSE, self)
                elif self.menu.active_type != MenuState.MAIN:
                    self.menu.open_menu(MenuState.MAIN, self)

            if self.slide_mode:
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    self.next_slide()
            elif self.is_playing:
                self.ui.handle_event(event, self)
            else:
                self.menu.handle_event(event, self)

    def get_scaled_mouse(self):
        window_width, window_height = self.screen.get_size()
        scale_x = window_width / self.native_size[0]
        scale_y = window_height / self.native_size[1]
        scale = min(scale_x, scale_y)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        scaled_x = (mouse_x - (window_width - self.native_size[0] * scale) / 2) / scale
        scaled_y = (mouse_y - (window_height - self.native_size[1] * scale) / 2) / scale

        return int(scaled_x), int(scaled_y)

    def update(self):
        """Updates all game objects and logic."""
        if self.slide_mode:
            self.slide_timer += 1
            total_time = self.slide_fade_duration * 2 + self.slide_display_duration
            if self.slide_timer >= total_time:
                self.slide_timer = 0
                self.next_slide()
            return

        # Prevent crash if level not loaded yet
        if not self.level:
            return

        if self.is_playing:
            self.level.update(self.dt, self)
            self.camera.follow(self.level.player)
            self.ui.update(self.level.player)
            self.level.check_touch(self.level.player, self)

            if self.level.player.show_death_screen:
                self.menu.open_menu(MenuState.DEATH, self)

            if self.show_level_title:
                self.level_title_timer += 1
                if self.level_title_timer >= self.level_title_duration:
                    self.show_level_title = False

    def next_slide(self):
        """Progresses to the next slide in the current slide mode."""
        if self.slide_mode == "story":
            self.story_index += 1
            if self.story_index >= len(self.story_texts):
                self.slide_mode = "tutorial" if self.tutorial_images else None
        elif self.slide_mode == "tutorial":
            self.tutorial_index += 1
            if self.tutorial_index >= len(self.tutorial_images):
                self.slide_mode = None
                self.load_level(self.current_level)

    def render(self):
        """Renders everything on a fixed surface and scales it while keeping the aspect ratio."""
        self.scaled_surface.fill((0, 0, 0))

        if self.slide_mode == "story":
            self.render_story(self.scaled_surface)
        elif self.slide_mode == "tutorial":
            self.render_tutorial(self.scaled_surface)
        elif self.is_playing:
            for bg in self.backgrounds:
                bg.render(self.scaled_surface, self.camera)

            self.level.render(self.scaled_surface, self.camera)
            self.ui.render(self.scaled_surface)

            if self.show_level_title:
                self.render_level_title(self.scaled_surface)

            self.scaled_surface.blit(self.foreground, (0, 0))
        else:
            self.menu.render(self.scaled_surface, self)

        self.scale_and_center()
        pygame.display.flip()

    def render_story(self, screen):
        screen.fill((0, 0, 0))
        if self.story_index < len(self.story_texts):
            alpha = self.font_manager.fade_alpha(
                self.slide_timer,
                self.slide_fade_duration,
                self.slide_display_duration,
                self.slide_fade_duration
            )
            self.font_manager.render(
                text=self.story_texts[self.story_index],
                surface=screen,
                position=(screen.get_width() // 2, screen.get_height() // 2),
                size=24,
                wrap=True,
                max_width=screen.get_width() - 100,
                align_center=True,
                alpha=alpha
            )

    def render_tutorial(self, screen):
        screen.fill((0, 0, 0))
        if self.tutorial_index < len(self.tutorial_images):
            alpha = self.font_manager.fade_alpha(
                self.slide_timer,
                self.slide_fade_duration,
                self.slide_display_duration,
                self.slide_fade_duration
            )
            img = self.tutorial_images[self.tutorial_index].copy()
            img.set_alpha(alpha)
            rect = img.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(img, rect)

    def render_level_title(self, screen):
        alpha = self.font_manager.fade_alpha(
            self.level_title_timer,
            self.level_title_fade,
            self.level_title_duration - 2 * self.level_title_fade,
            self.level_title_fade
        )
        self.font_manager.render(
            surface=screen,
            text=self.level_title,
            position=(screen.get_width() // 2, screen.get_height() // 3),
            size=36,
            align_center=True,
            alpha=alpha
        )

    def scale_and_center(self):
        win_w, win_h = self.screen.get_size()
        scale = min(win_w / self.native_size[0], win_h / self.native_size[1])
        new_w = int(self.native_size[0] * scale)
        new_h = int(self.native_size[1] * scale)
        scaled = pygame.transform.scale(self.scaled_surface, (new_w, new_h))

        x = (win_w - new_w) // 2
        y = (win_h - new_h) // 2
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, (x, y))

    def run(self):
        while True:
            self.clock.tick(self.fps)
            self.handle_events()
            self.update()
            self.render()