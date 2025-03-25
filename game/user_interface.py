import pygame
import os
import json

from game.menu.menu import MenuState


class UI:
    def __init__(self):
        """Initializes UI elements (health, pause button)."""
        self.font = pygame.font.Font(None, 36)

        # Load UI configuration
        with open("assets/ui/ui.json") as f:
            ui_data = json.load(f)

        # Load images
        self.heart_full = pygame.image.load(os.path.join("assets/ui", ui_data["heart_full"])).convert_alpha()
        self.heart_half = pygame.image.load(os.path.join("assets/ui", ui_data["heart_half"])).convert_alpha()
        self.heart_empty = pygame.image.load(os.path.join("assets/ui", ui_data["heart_empty"])).convert_alpha()
        self.ability_icons = {}
        self.ability_size = 30
        for key, path in ui_data["abilities"].items():
            icon = pygame.image.load(os.path.join("assets/ui", path)).convert_alpha()
            icon = pygame.transform.scale(icon, (self.ability_size,self.ability_size))
            self.ability_icons[key] = icon

        # UI sizes
        self.heart_size = ui_data["heart_size"]
        self.pause_size = ui_data["pause_size"]

        # Scale UI elements
        self.heart_full = pygame.transform.scale(self.heart_full, (self.heart_size, self.heart_size))
        self.heart_half = pygame.transform.scale(self.heart_half, (self.heart_size, self.heart_size))
        self.heart_empty = pygame.transform.scale(self.heart_empty, (self.heart_size, self.heart_size))

        # Default player stats
        self.abilities = None
        self.health = 6
        self.max_health = 6

        # Glitchy Pause Button
        self.pause_icons = self.load_button_images(ui_data)
        self.hovering = False
        self.pause_frame = 0
        self.frame_timer = 0

        self.player = None

    def update(self, player):
        """Updates UI values based on the player state."""
        self.health = max(0, min(player.health, self.max_health))
        self.mouse_pos = pygame.mouse.get_pos()
        self.abilities = player.abilities

    def pause_hovering(self, sprites_list):
        out = sprites_list[self.pause_frame]
        self.frame_timer += 1
        if self.frame_timer % 4 == 0:
            self.pause_frame += 1 if self.pause_frame < len(sprites_list)-1 else 0
        return out

    def render(self, screen):
        """Renders the UI elements on the screen (fixed position)."""
        screen_width, _ = screen.get_size()

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
        pause_hover_list = self.pause_icons["hover"]
        pause_rect = pygame.Rect(20, 20, self.pause_size, self.pause_size)
        mouse_pos = pause_rect.collidepoint(self.mouse_pos)
        if mouse_pos:
            screen.blit(self.pause_hovering(pause_hover_list), (20,20))
        else:
            self.frame_timer = 0
            self.pause_frame = 0
            screen.blit(self.pause_icons["idle"], (20,20))

        self.render_abilities(screen, self.abilities)

    def render_abilities(self, screen, abilities):
        """Render ability icons with cooldown overlay and glow if ready."""
        x = 20  # Start from bottom-left
        y = screen.get_height() - 40  # Leave some margin from bottom

        for name, ability in abilities.items():
            icon = self.ability_icons.get(name)
            if icon is None:
                continue

            # Draw the icon
            screen.blit(icon, (x, y))

            # Draw cooldown overlay if on cooldown
            if ability.current_cooldown > 0:
                ratio = ability.current_cooldown / ability.cooldown
                height = int(self.ability_size * ratio)
                cooldown_overlay = pygame.Surface((self.ability_size, height), pygame.SRCALPHA)
                cooldown_overlay.fill((0, 0, 0, 128))
                screen.blit(cooldown_overlay, (x, y + (self.ability_size - height)))

            x += 40

    def handle_event(self, event, engine):
        """Handles UI interactions (pause button)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pause_rect = pygame.Rect(20, 20, self.pause_size, self.pause_size)
            if pause_rect.collidepoint(event.pos):
                engine.menu.toggle_menu(MenuState.PAUSE, engine)

    @staticmethod
    def load_button_images(data):
        frames = []
        play_button_sheet = pygame.image.load(os.path.join("assets/ui", data["pause"])).convert_alpha()
        width = data["pause_size"]
        height = play_button_sheet.get_height()
        for i in range(play_button_sheet.get_width() // width):
            frames.append(play_button_sheet.subsurface(pygame.Rect(i * width, 0, width, height)))
        play_button_list = {"idle": frames[0], "hover": frames[1:] if len(frames) > 1 else frames[0]}
        return play_button_list