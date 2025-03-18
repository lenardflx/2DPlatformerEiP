import pygame
import os
import json

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)

        with open("assets/ui/ui.json") as f:
            ui_data = json.load(f)

        self.heart_full = pygame.image.load(os.path.join("assets/ui", ui_data["heart_full"])).convert_alpha()
        self.heart_half = pygame.image.load(os.path.join("assets/ui", ui_data["heart_half"])).convert_alpha()
        self.heart_empty = pygame.image.load(os.path.join("assets/ui", ui_data["heart_empty"])).convert_alpha()
        self.coin_icon = pygame.image.load(os.path.join("assets/ui", ui_data["coin"])).convert_alpha()
        self.pause_icon = pygame.image.load(os.path.join("assets/ui", ui_data["pause"])).convert_alpha()

        self.heart_size = ui_data["heart_size"]
        self.coin_size = ui_data["coin_size"]
        self.pause_size = ui_data["pause_size"]

        self.heart_full = pygame.transform.scale(self.heart_full, (self.heart_size, self.heart_size))
        self.heart_half = pygame.transform.scale(self.heart_half, (self.heart_size, self.heart_size))
        self.heart_empty = pygame.transform.scale(self.heart_empty, (self.heart_size, self.heart_size))

        self.coin_icon = pygame.transform.scale(self.coin_icon, (self.coin_size, self.coin_size))
        self.pause_icon = pygame.transform.scale(self.pause_icon, (self.pause_size, self.pause_size))

        self.health = 4
        self.max_health = 6
        self.coins = 0

    def update(self, player):
        self.health = max(0, min(player.health, self.max_health))
        self.coins = player.coins

    def render(self, x_offset, y_offset, scaled_width, scaled_height):
        heart_x = x_offset + scaled_width - 40
        heart_y = y_offset + 20

        total_hearts = self.max_health // 2
        has_half_heart = self.health % 2 == 1
        empty_hearts = total_hearts - self.health // 2 - has_half_heart

        for i in range(total_hearts):
            if empty_hearts:
                self.screen.blit(self.heart_empty, (heart_x, heart_y))
                empty_hearts -= 1
            elif has_half_heart:
                self.screen.blit(self.heart_half, (heart_x, heart_y))
                has_half_heart = False
            else:
                self.screen.blit(self.heart_full, (heart_x, heart_y))
            heart_x -= self.heart_size + 5

        coin_x = x_offset + scaled_width - 100
        coin_y = heart_y + self.heart_size + 10
        self.screen.blit(self.coin_icon, (coin_x, coin_y))

        coin_text = self.font.render(f"{self.coins}", True, (255, 255, 255))
        self.screen.blit(coin_text, (coin_x + 50, coin_y + 10))

        self.screen.blit(self.pause_icon, (x_offset + 20, y_offset + 20))

    def handle_events(self, event, engine):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(20, 20, self.pause_size, self.pause_size).collidepoint(event.pos):
                print("Pause gedrückt!")
