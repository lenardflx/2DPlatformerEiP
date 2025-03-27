import pygame
import os
import json
from time import time
from game.menu.menu import MenuState


class UI:
    def __init__(self, font_manager, sound_manager):
        """Initializes UI with optimized asset loading and caching."""
        self.font_manager = font_manager
        self.sound_manager = sound_manager

        with open("assets/ui/ui.json") as f:
            ui_data = json.load(f)

        # Sizes
        self.heart_size = ui_data["heart_size"]
        self.button_size = ui_data["button_size"]

        # Load and scale heart & skull icons
        self.heart_full = self._load_icon(ui_data["heart_full"], self.heart_size)
        self.heart_half = self._load_icon(ui_data["heart_half"], self.heart_size)
        self.heart_empty = self._load_icon(ui_data["heart_empty"], self.heart_size)
        self.skull_icon = self._load_icon(ui_data["skull_icon"], 16)

        # Load ability icons
        self.ability_icons = {
            name: self._load_icon(path, self.button_size)
            for name, path in ui_data["abilities"].items()
        }

        # Pause Button Frames
        self.pause_icons = self._load_pause_frames(ui_data)
        self.pause_frame = 0
        self.frame_timer = 0

        # Cooldown overlay surface (shared, scaled per draw)
        self.cooldown_overlay = pygame.Surface(
            (self.button_size, self.button_size), pygame.SRCALPHA
        )
        self.cooldown_overlay.fill((0, 0, 0, 128))

        # State
        self.mouse_pos = (0, 0)
        self.health = 6
        self.max_health = 6
        self.abilities = None
        self.total_enemies = 0
        self.killed_enemies = 0
        self.time_elapsed = 0

        # Cached text
        self.last_timer_text = ""
        self.last_kill_text = ""
        self.cached_timer_surface = None
        self.cached_kill_surface = None

    def _load_icon(self, filename, size):
        path = os.path.join("assets/ui", filename)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (size, size))

    def _load_pause_frames(self, ui_data):
        sheet = pygame.image.load(os.path.join("assets/ui", ui_data["pause"])).convert_alpha()
        width = self.button_size
        height = sheet.get_height()
        frames = [sheet.subsurface(pygame.Rect(i * width, 0, width, height))
                  for i in range(sheet.get_width() // width)]
        return {
            "idle": frames[0],
            "hover": frames[1:] if len(frames) > 1 else [frames[0]]
        }

    def update(self, player):
        """Updates internal state from player."""
        self.mouse_pos = pygame.mouse.get_pos()
        self.health = max(0, min(player.health, self.max_health))
        self.abilities = player.abilities
        self.time_elapsed = time() - player.level.start_time
        self.total_enemies = player.level.enemies_count
        self.killed_enemies = max(0, self.total_enemies - len(player.level.enemies))

    def handle_event(self, event, engine):
        """Pause button input handling."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pause_rect = pygame.Rect(20, 20, self.button_size, self.button_size)
            if pause_rect.collidepoint(event.pos):
                engine.menu.toggle_menu(MenuState.PAUSE, engine)
                self.sound_manager.play_sfx("button_click")

    def render(self, screen):
        screen_width, screen_height = screen.get_size()
        self._render_health(screen, screen_width)
        self._render_pause_button(screen)
        self._render_abilities(screen, screen_height)
        self._render_timer(screen)
        self._render_kill_counter(screen, screen_width)

    def _render_health(self, screen, screen_width):
        x = screen_width - 40
        y = 20
        full = self.health // 2
        half = self.health % 2
        total = self.max_health // 2

        for _ in range(total):
            if full > 0:
                screen.blit(self.heart_full, (x, y))
                full -= 1
            elif half:
                screen.blit(self.heart_half, (x, y))
                half = 0
            else:
                screen.blit(self.heart_empty, (x, y))
            x -= self.heart_size + 5

    def _render_pause_button(self, screen):
        pos = (20, 20)
        pause_rect = pygame.Rect(*pos, self.button_size, self.button_size)

        if pause_rect.collidepoint(self.mouse_pos):
            screen.blit(self._pause_hovering(), pos)
        else:
            self.frame_timer = 0
            self.pause_frame = 0
            screen.blit(self.pause_icons["idle"], pos)

    def _pause_hovering(self):
        if self.frame_timer % 4 == 0 and self.pause_frame < len(self.pause_icons["hover"]) - 1:
            self.pause_frame += 1
        self.frame_timer += 1
        return self.pause_icons["hover"][self.pause_frame]

    def _render_abilities(self, screen, screen_height):
        if not self.abilities:
            return
        x = 20
        y = screen_height - 40

        for name, ability in self.abilities.items():
            icon = self.ability_icons.get(name)
            if not icon:
                continue

            screen.blit(icon, (x, y))

            if ability.current_cooldown > 0:
                ratio = ability.current_cooldown / ability.cooldown
                height = int(self.button_size * ratio)
                src = pygame.Rect(0, self.button_size - height, self.button_size, height)
                screen.blit(self.cooldown_overlay, (x, y + self.button_size - height), area=src)

            x += 40

    def _render_timer(self, screen):
        minutes = int(self.time_elapsed / 60)
        seconds = self.time_elapsed % 60
        timer_text = f"{minutes}:{seconds:.2f}"

        if timer_text != self.last_timer_text:
            self.last_timer_text = timer_text
            self.cached_timer_surface = self.font_manager.render_to_surface(
                timer_text, size=32
            )

        if self.cached_timer_surface:
            x = screen.get_width() // 2 - self.cached_timer_surface.get_width() // 2
            screen.blit(self.cached_timer_surface, (x, 30))

    def _render_kill_counter(self, screen, width):
        kill_text = f"{self.killed_enemies}/{self.total_enemies}"

        if kill_text != self.last_kill_text:
            self.last_kill_text = kill_text
            self.cached_kill_surface = self.font_manager.render_to_surface(
                kill_text, size=24
            )

        center_x = width // 2
        skull_y = 65
        screen.blit(self.skull_icon, (center_x - 30, skull_y))
        screen.blit(self.cached_kill_surface, (center_x, skull_y + 1))
