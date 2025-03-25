import pygame
import os
import json

from game.menu.menu import MenuState


class UI:
    def __init__(self):
        """Initializes UI elements (health, coins, pause button)."""
        self.font = pygame.font.Font(None, 36)

        # Load UI configuration
        with open("assets/ui/ui.json") as f:
            ui_data = json.load(f)

        # Load images
        self.heart_full = pygame.image.load(os.path.join("assets/ui", ui_data["heart_full"])).convert_alpha()
        self.heart_half = pygame.image.load(os.path.join("assets/ui", ui_data["heart_half"])).convert_alpha()
        self.heart_empty = pygame.image.load(os.path.join("assets/ui", ui_data["heart_empty"])).convert_alpha()
        self.coin_icon = pygame.image.load(os.path.join("assets/ui", ui_data["coin"])).convert_alpha()
        self.pause_icon = pygame.image.load(os.path.join("assets/ui", ui_data["pause"])).convert_alpha()
        self.ability_icons = {}
        self.ability_size = 30
        for key, path in ui_data["abilities"].items():
            icon = pygame.image.load(os.path.join("assets/ui", path)).convert_alpha()
            icon = pygame.transform.scale(icon, (self.ability_size,self.ability_size))
            self.ability_icons[key] = icon

        # UI sizes
        self.heart_size = ui_data["heart_size"]
        self.coin_size = ui_data["coin_size"]
        self.pause_size = ui_data["pause_size"]

        # Scale UI elements
        self.heart_full = pygame.transform.scale(self.heart_full, (self.heart_size, self.heart_size))
        self.heart_half = pygame.transform.scale(self.heart_half, (self.heart_size, self.heart_size))
        self.heart_empty = pygame.transform.scale(self.heart_empty, (self.heart_size, self.heart_size))
        self.coin_icon = pygame.transform.scale(self.coin_icon, (self.coin_size, self.coin_size))
        self.pause_icon = pygame.transform.scale(self.pause_icon, (self.pause_size, self.pause_size))

        # Default player stats
        self.abilities = None
        self.health = 6
        self.max_health = 6
        self.coins = 0

        self.player = None

    def update(self, player):
        """Updates UI values based on the player state."""
        self.health = max(0, min(player.health, self.max_health))
        self.coins = player.coins
        self.abilities = player.abilities

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

        # Coin display
        coin_x = screen_width - 100
        coin_y = heart_y + self.heart_size + 10
        screen.blit(self.coin_icon, (coin_x, coin_y))

        coin_text = self.font.render(f"{self.coins}", True, (255, 255, 255))
        screen.blit(coin_text, (coin_x + 50, coin_y + 10))

        # Pause button
        screen.blit(self.pause_icon, (20, 20))

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
                engine.menu_state = MenuState.PAUSE
                engine.is_playing = False
                print("Game Paused!")
