import json
import pygame

from core.camera import Camera
from core.font import FontManager
from core.game_data import get_game_data
from game.background import Background
from game.levels import Level
from game.menu import Menu, MenuState
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

        # Game State
        self.level = None
        self.current_level = None
        self.is_playing = False
        self.showing_story = False
        self.showing_tutorial = False

        # Data
        self.levels_data = None
        self.level_count = None
        self.completed_levels = []  # TODO: Load/save from persistent file
        self.load_level_metadata()

        # Font/UI
        self.font_manager = FontManager(self.native_size)
        self.ui = UI()
        self.menu = Menu(self.native_size, self.controls)
        self.menu.active_type = MenuState.MAIN

        # Story settings
        self.story_texts = []
        self.story_index = 0
        self.story_timer = 0
        self.story_skip_hold = 0
        self.story_fade_duration = 45
        self.story_display_duration = 200

        # Tutorial
        self.tutorial_slide = 0
        self.tutorial_total = 3

        # Level title
        self.show_level_title = False
        self.level_title_timer = 0
        self.level_title_duration = 200
        self.level_title_fade = 30
        self.level_title = ""

        # Background
        with open("assets/background/background.json") as f:
            bg_data = json.load(f)
        self.backgrounds = [Background(d) for d in bg_data[::-1]]

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
        last = self.completed_levels[-1]
        return (last + 1) % self.level_count

    def start_game(self):
        """Starts the game from current level."""
        if not self.completed_levels:
            self.showing_tutorial = True
        else:
            self.load_story_intro(self.next_level)
        self.is_playing = True
        self.menu.active_type = None

    def load_level(self, level_id):
        """Loads a level by ID."""
        self.level = Level(level_id, self.controls)
        self.camera = Camera(self.native_size[0], self.native_size[1], self.level.width, self.level.height)
        self.show_level_title = True
        self.level_title_timer = 0
        self.level_title = self.levels_data.get(str(level_id), {}).get("title", f"Level {level_id + 1}")

    def load_story_intro(self, level_id):
        """Loads the story intro for a level."""
        self.showing_story = True
        self.story_index = 0
        self.story_timer = 0
        self.story_skip_hold = 0
        self.current_level = level_id
        self.story_texts = self.levels_data.get(str(level_id), {}).get("story", [])

    def handle_events(self):
        """Handles all game events like input and window resizing."""
        for event in pygame.event.get():  # Process one event at a time
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if self.controls.is_action_active("menu"):
                self.menu.toggle_menu(MenuState.PAUSE, self)

            keys = pygame.key.get_pressed()

            if self.is_playing:
                if self.showing_story:
                    if keys[pygame.K_SPACE]:
                        self.story_skip_hold += 1
                        if self.story_skip_hold > 30:
                            self.showing_story = False
                            self.load_level(self.current_level)
                    else:
                        self.story_skip_hold = 0

                    if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            self.story_index += 1
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.story_index += 1

                        if self.story_index >= len(self.story_texts):
                            self.showing_story = False
                            self.load_level(self.current_level)

                elif self.showing_tutorial:
                    if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                        self.tutorial_slide += 1
                        if self.tutorial_slide > self.tutorial_total:
                            self.showing_tutorial = False
                            self.load_story_intro(0)
                else:
                    self.ui.handle_event(event, self)
            else:
                self.menu.handle_event(event, self)

    def update(self):
        """Updates all game objects and logic."""
        if self.is_playing and self.showing_story:
            self.story_timer += 1
            total_time = self.story_fade_duration * 2 + self.story_display_duration
            if self.story_timer >= total_time:
                self.story_timer = 0
                self.story_index += 1
                if self.story_index >= len(self.story_texts):
                    self.showing_story = False
                    self.load_level(self.current_level)

        elif self.is_playing and not self.showing_tutorial:
            self.level.update(self.dt, self)
            self.camera.follow(self.level.player)
            self.ui.update(self.level.player)
            self.level.check_touch(self.level.player, self)

            if self.level.player.health <= 0:
                self.menu.active_type = MenuState.DEATH
                self.is_playing = False

        if self.show_level_title:
            self.level_title_timer += 1
            if self.level_title_timer >= self.level_title_duration:
                self.show_level_title = False

    def render(self):
        """Renders everything on a fixed surface and scales it while keeping the aspect ratio."""
        self.scaled_surface.fill((0, 0, 0))

        if self.is_playing:
            if self.showing_tutorial:
                self.render_tutorial(self.scaled_surface)
            elif self.showing_story:
                self.render_story(self.scaled_surface)
            else:
                for bg in self.backgrounds:
                    bg.render(self.scaled_surface, self.camera)
                self.level.render(self.scaled_surface, self.camera)
                self.ui.render(self.scaled_surface)
                if self.show_level_title:
                    self.render_level_title(self.scaled_surface)
        else:
            self.menu.render(self.scaled_surface)

        self.scale_and_center()
        pygame.display.flip()

    def render_story(self, screen):
        screen.fill((0, 0, 0))

        if 0 <= self.story_index < len(self.story_texts):
            text = self.story_texts[self.story_index]
            alpha = self.font_manager.fade_alpha(
                self.story_timer,
                self.story_fade_duration,
                self.story_display_duration,
                self.story_fade_duration
            )

            self.font_manager.render(
                surface=screen,
                text=text,
                position=(screen.get_width() // 2, screen.get_height() // 2),
                size=24,
                wrap=True,
                max_width=screen.get_width() - 100,
                align_center=True,
                alpha=alpha
            )

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

    def render_tutorial(self, screen):
        slides = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        color = slides[self.tutorial_slide % len(slides)]
        screen.fill(color)

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