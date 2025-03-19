import json
import os
import pygame

class MenuOptions:
    START = 0
    PAUSE = 1
    DEATH = 2
    SETTINGS = 3
    LEVELS = 4

class Menu:
    def __init__(self):
        with open("assets/menu/menu.json") as f:
            menu_data = json.load(f)

        self.active_type = MenuOptions.START
        self.last_frame = None

        self.menu_layouts = {
            MenuOptions.START: ["continue", "levels", "settings", "exit"],
            MenuOptions.PAUSE: ["resume", "retry", "settings", "main_menu"],
            MenuOptions.DEATH: ["retry", "main_menu"],
            MenuOptions.SETTINGS: ["controls"],
            MenuOptions.LEVELS: []
        }

        self.button_image = pygame.image.load(os.path.join("assets/menu", menu_data["button_image"])).convert_alpha()
        self.button_hover_image = pygame.image.load(
            os.path.join("assets/menu", menu_data["button_hover_image"])).convert_alpha()

        self.buttons = {}
        for key in set(sum(self.menu_layouts.values(), [])):
            self.buttons[key] = {
                "rect": pygame.Rect(0, 0, self.button_image.get_width(), self.button_image.get_height()),
                "hovered": False,
                "text": key.replace("_", " ").title()
            }

    def handle_events(self, engine):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for key, button in self.buttons.items():
                    if button["rect"].collidepoint(event.pos):
                        self.handle_button_action(key, engine)

        for key, button in self.buttons.items():
            button["hovered"] = button["rect"].collidepoint(mouse_pos)

    def handle_button_action(self, key, engine):
        if key == "continue" or key == "resume":
            engine.is_menu = False
        elif key == "retry":
            engine.reset_game()
        elif key == "main_menu" or key == "exit":
            engine.is_menu = True
            self.open_menu(MenuOptions.START, engine)
        elif key == "settings":
            self.open_menu(MenuOptions.SETTINGS, engine)
        elif key == "levels":
            self.open_menu(MenuOptions.LEVELS, engine)
        elif key == "exit":
            engine.is_running = False

    def render(self, screen):
        if self.active_type == MenuOptions.START:
            screen.fill((0, 0, 255))
        else:
            if self.last_frame:
                screen.blit(self.last_frame, (0, 0))

            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            if self.active_type == MenuOptions.DEATH:
                overlay.fill((255, 0, 0, 128))
                self.render_text(screen, "You Died", screen.get_width() // 2, 100, size=50)
            else:
                overlay.fill((128, 128, 128, 128))
            screen.blit(overlay, (0, 0))

        screen_width, screen_height = screen.get_size()
        button_spacing = 80
        menu_buttons = self.menu_layouts.get(self.active_type, [])

        for i, key in enumerate(menu_buttons):
            button = self.buttons[key]
            image = self.button_hover_image if button["hovered"] else self.button_image

            rect = image.get_rect()
            rect.center = (screen_width // 2, screen_height // 2 + i * button_spacing)
            button["rect"] = rect

            screen.blit(image, rect)
            self.render_text(screen, button["text"], rect.centerx, rect.centery)

    def render_text(self, screen, text, x, y, size=30, color=(255, 255, 255)):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    def open_menu(self, menu_type, engine):
        self.active_type = menu_type
        if not engine.is_menu:
            self.last_frame = engine.screen.copy()
        engine.is_menu = True
