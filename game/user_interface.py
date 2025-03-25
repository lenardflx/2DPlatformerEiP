from time import time

import pygame
import os
import json

from game.menu.menu import MenuState


class UI:
    def __init__(self, font_manager, sound_manager):
        """Initializes UI elements (health, pause button)."""
        self.font_manager = font_manager
        self.sound_manager = sound_manager
        # Load UI configuration
        with open("assets/ui/ui.json") as f:
            ui_data = json.load(f)

        # UI sizes
        self.heart_size = ui_data["heart_size"]
        self.button_size = ui_data["button_size"]

        # Load images
        self.heart_full = pygame.image.load(os.path.join("assets/ui", ui_data["heart_full"])).convert_alpha()
        self.heart_half = pygame.image.load(os.path.join("assets/ui", ui_data["heart_half"])).convert_alpha()
        self.heart_empty = pygame.image.load(os.path.join("assets/ui", ui_data["heart_empty"])).convert_alpha()
        self.skull_icon = pygame.image.load(os.path.join("assets/ui", ui_data["skull_icon"])).convert_alpha()

        self.ability_icons = {}
        for key, path in ui_data["abilities"].items():
            icon = pygame.image.load(os.path.join("assets/ui", path)).convert_alpha()
            icon = pygame.transform.scale(icon, (self.button_size, self.button_size))
            self.ability_icons[key] = icon

        # Scale UI elements
        self.heart_full = pygame.transform.scale(self.heart_full, (self.heart_size, self.heart_size))
        self.heart_half = pygame.transform.scale(self.heart_half, (self.heart_size, self.heart_size))
        self.heart_empty = pygame.transform.scale(self.heart_empty, (self.heart_size, self.heart_size))
        self.skull_icon = pygame.transform.scale(self.skull_icon, (16,16))

        # Default stats
        self.abilities = None
        self.health = 6
        self.max_health = 6
        self.total_enemies = 0
        self.killed_enemies = 0

        # Glitchy Pause Button
        self.pause_icons = self.load_button_images(ui_data)
        self.pause_frame = 0
        self.frame_timer = 0
        self.mouse_pos = (0, 0)
        self.time_elapsed = 0

    def update(self, player):
        """Updates UI values based on the player state."""
        self.mouse_pos = pygame.mouse.get_pos()
        self.health = max(0, min(player.health, self.max_health))
        self.abilities = player.abilities
        self.time_elapsed = time() - player.level.start_time
        self.total_enemies = player.level.enemies_count
        self.killed_enemies = player.level.enemies_count - len(player.level.enemies)

    def pause_hovering(self, sprites_list):
        out = sprites_list[self.pause_frame]
        self.frame_timer += 1
        if self.frame_timer % 4 == 0:
            self.pause_frame += 1 if self.pause_frame < len(sprites_list)-1 else 0
        return out

    def render(self, screen):
        """Renders the UI elements on the screen (fixed position)."""
        screen_width, screen_height = screen.get_size()

        # Health display
        heart_x = screen_width - 40
        heart_y = 20
        total_hearts = self.max_health // 2
        hearts_drawn = self.health // 2
        has_half_heart = self.health % 2 == 1

        for _ in range(total_hearts):
            if hearts_drawn > 0:
                screen.blit(self.heart_full, (heart_x, heart_y))
                hearts_drawn -= 1
            elif has_half_heart:
                screen.blit(self.heart_half, (heart_x, heart_y))
                has_half_heart = False
            else:
                screen.blit(self.heart_empty, (heart_x, heart_y))
            heart_x -= self.heart_size + 5

        # Pause button
        pause_rect = pygame.Rect(20, 20, self.button_size, self.button_size)
        if pause_rect.collidepoint(self.mouse_pos):
            screen.blit(self.pause_hovering(self.pause_icons["hover"]), (20, 20))
        else:
            self.frame_timer = 0
            self.pause_frame = 0
            screen.blit(self.pause_icons["idle"], (20, 20))

        self.render_abilities(screen, self.abilities, screen_height)
        self.render_timer(screen)
        self.render_kill_counter(screen, screen_width)

    def render_abilities(self, screen, abilities, screen_height):
        """Render ability icons with cooldown overlay and glow if ready."""
        x = 20  # Start from bottom-left
        y = screen_height - 40  # Leave some margin from bottom

        for name, ability in abilities.items():
            icon = self.ability_icons.get(name)
            if icon is None:
                continue

            # Draw the icon
            screen.blit(icon, (x, y))

            # Draw cooldown overlay if on cooldown
            if ability.current_cooldown > 0:
                ratio = ability.current_cooldown / ability.cooldown
                height = int(self.button_size * ratio)
                cooldown_overlay = pygame.Surface((self.button_size, height), pygame.SRCALPHA)
                cooldown_overlay.fill((0, 0, 0, 128))
                screen.blit(cooldown_overlay, (x, y + (self.button_size - height)))

            x += 40

    def render_timer(self, screen):
        minutes = int(self.time_elapsed / 60)
        seconds = self.time_elapsed % 60
        timer_text = f"{minutes}:{seconds:.2f}"
        center_x = screen.get_width() // 2
        self.font_manager.render(screen, timer_text, position=(center_x, 30), size=32, align_center=True)

    def render_kill_counter(self, screen, width):
        """Displays skull icon and kill count (e.g., 5 / 8) under the timer."""
        center_x = width // 2
        skull_y = 65  # a bit under the timer

        kill_text = f"{self.killed_enemies}/{self.total_enemies}"

        # Positioning: icon and text side by side
        icon_x = center_x - 30
        text_x = center_x

        screen.blit(self.skull_icon, (icon_x, skull_y))
        self.font_manager.render(screen, kill_text, position=(text_x, skull_y + 1), size=24, align_center=False)


    def handle_event(self, event, engine):
        """Handles UI interactions (pause button)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pause_rect = pygame.Rect(20, 20, self.button_size, self.button_size)
            if pause_rect.collidepoint(event.pos):
                engine.menu.toggle_menu(MenuState.PAUSE, engine)
                self.sound_manager.play_sfx("button_click")

    @staticmethod
    def load_button_images(data):
        frames = []
        sheet = pygame.image.load(os.path.join("assets/ui", data["pause"])).convert_alpha()
        width = data["button_size"]
        height = sheet.get_height()
        for i in range(sheet.get_width() // width):
            frames.append(sheet.subsurface(pygame.Rect(i * width, 0, width, height)))
        return {
            "idle": frames[0],
            "hover": frames[1:] if len(frames) > 1 else [frames[0]],
        }