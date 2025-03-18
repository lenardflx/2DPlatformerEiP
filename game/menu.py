import json
import os
import pygame

class MenuOptions:
    START = 0
    PAUSE = 1
    DEATH = 2

class Menu:
    def __init__(self):
        with open("assets/menu/menu.json") as f:
            menu_data = json.load(f)

        self.active_type = MenuOptions.START

        self.start_button = pygame.image.load(os.path.join("assets/menu", menu_data["start_button"])).convert_alpha()
        self.start_button_rect = self.start_button.get_rect()

        # self.settings_button =
        # self.settings_button_rect = self.settings_button.get_rect()

        self.quit_button = pygame.image.load(os.path.join("assets/menu", menu_data["quit_button"])).convert_alpha()
        self.quit_button_rect = self.quit_button.get_rect()

    def handle_events(self, engine):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.is_running = False
            elif event.type == pygame.VIDEORESIZE:
                self.update_layout(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button_rect.collidepoint(event.pos):
                    engine.is_menu = False
                elif self.quit_button_rect.collidepoint(event.pos):
                    engine.is_running = False

    def update_layout(self, screen_width, screen_height):
        button_spacing = 80
        self.start_button_rect.center = (screen_width // 2, screen_height // 2 - button_spacing)
        self.quit_button_rect.center = (screen_width // 2, screen_height // 2 - (button_spacing * 1/3))

    def render(self, screen):
        screen.fill((30, 30, 30))
        screen.blit(self.start_button, self.start_button_rect)
        screen.blit(self.quit_button, self.quit_button_rect)

    def open_menu(self, menu_type,engine):
        self.active_type=menu_type
        engine.is_menu=True