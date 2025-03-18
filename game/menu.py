import json
import os
import pygame

class Menu:
    def __init__(self):
        with open("assets/menu/menu.json") as f:
            menu_data = json.load(f)

        self.start_button = pygame.image.load(os.path.join("assets/menu", menu_data["start_button"])).convert_alpha()
        self.start_button_rect = self.start_button.get_rect()
        self.start_button_rect.center = (400, 400)

    def handle_events(self, engine):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.is_running = False
            elif event.type == pygame.VIDEORESIZE:
                self.update_layout(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button_rect.collidepoint(event.pos):
                    engine.is_menu = False

    def update_layout(self, screen_width, screen_height):
        button_spacing = 80
        self.start_button_rect.center = (screen_width // 2, screen_height // 2 - button_spacing)

    def render(self, screen):
        screen.fill((30, 30, 30))
        screen.blit(self.start_button, self.start_button_rect)
