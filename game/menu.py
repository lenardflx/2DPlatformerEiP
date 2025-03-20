import json
import os
import pygame

class MenuState:
    NONE = 0
    START = 1
    PAUSE = 2
    DEATH = 3
    SETTINGS = 4
    LEVELS = 5

class Menu:
    def __init__(self, screen_size):
        """Initializes the menu system and loads UI assets."""
        with open("assets/menu/menu.json") as f:
            menu_data = json.load(f)

        self.active_type = MenuState.START
        self.last_frame = None
        self.screen_size = screen_size

        # Define button layouts for different menu types
        self.menu_layouts = {
            MenuState.START: ["continue", "levels", "settings", "exit"],
            MenuState.PAUSE: ["resume", "retry", "settings", "main_menu"],
            MenuState.DEATH: ["retry", "main_menu"],
            MenuState.SETTINGS: ["controls"],
            MenuState.LEVELS: []
        }

        # Load button images
        self.button_image = pygame.image.load(os.path.join("assets/menu", menu_data["button_image"])).convert_alpha()
        self.button_hover_image = pygame.image.load(
            os.path.join("assets/menu", menu_data["button_hover_image"])
        ).convert_alpha()

        # Generate button dictionary
        self.buttons = {}
        for key in set(sum(self.menu_layouts.values(), [])):  # Flatten the menu layout lists
            self.buttons[key] = {
                "rect": pygame.Rect(0, 0, self.button_image.get_width(), self.button_image.get_height()),
                "hovered": False,
                "text": key.replace("_", " ").title()
            }

    def handle_event(self, event, engine):
        """Handles a single event for menu interactions, adjusting for screen scaling."""
        mouse_x, mouse_y = self.scale_mouse_position(engine)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for key, button in self.buttons.items():
                    if button["rect"].collidepoint((mouse_x, mouse_y)):
                        self.handle_button_action(key, engine)

        # Check hover state
        for key, button in self.buttons.items():
            button["hovered"] = button["rect"].collidepoint((mouse_x, mouse_y))

    @staticmethod
    def scale_mouse_position(engine):
        """Converts mouse position to match the scaled UI layout."""
        window_width, window_height = engine.screen.get_size()
        scale_x = window_width / engine.native_size[0]
        scale_y = window_height / engine.native_size[1]
        scale = min(scale_x, scale_y)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Convert mouse coordinates to scaled space
        scaled_x = (mouse_x - (window_width - engine.native_size[0] * scale) / 2) / scale
        scaled_y = (mouse_y - (window_height - engine.native_size[1] * scale) / 2) / scale

        return int(scaled_x), int(scaled_y)

    def handle_button_action(self, key, game_engine):
        """Handles button clicks."""
        if key in ["continue", "resume"]:
            game_engine.is_playing = True
            self.active_type = MenuState.NONE
        elif key == "retry":
            game_engine.load_next_level()
            game_engine.is_playing = True
            self.active_type = MenuState.NONE
        elif key == "main_menu":
            self.active_type = MenuState.START
            game_engine.is_playing = False
        elif key == "settings":
            self.open_menu(MenuState.SETTINGS, game_engine)
        elif key == "levels":
            self.open_menu(MenuState.LEVELS, game_engine)
        elif key == "exit":
            pygame.quit()
            exit()

    def render(self, screen):
        """Renders the menu on the screen."""
        if self.active_type == MenuState.NONE:
            return

        if self.last_frame:
            screen.blit(self.last_frame, (0, 0))

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((128, 128, 128, 128))
        screen.blit(overlay, (0, 0))

        # Center menu buttons
        screen_width, screen_height = screen.get_size()
        button_spacing = 80
        menu_buttons = self.menu_layouts.get(self.active_type, [])

        for i, key in enumerate(menu_buttons):
            button = self.buttons[key]
            image = self.button_hover_image if button["hovered"] else self.button_image

            rect = image.get_rect()
            rect.center = (screen_width // 2, screen_height // 2 + i * button_spacing - len(menu_buttons) * 20)
            button["rect"] = rect

            screen.blit(image, rect)
            self.render_text(screen, button["text"], rect.centerx, rect.centery)

    def render_text(self, screen, text, x, y, size=30, color=(255, 255, 255)):
        """Renders centered text at a given position."""
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    def open_menu(self, menu_type, engine):
        """Opens a specific menu type and captures the current game screen for overlay effects."""
        # Capture the current game screen before opening the menu
        if self.active_type == MenuState.NONE:
            window_width, window_height = engine.screen.get_size()
            scale = min(window_width / self.screen_size[0], window_height / self.screen_size[1])
            new_width = int(self.screen_size[0] * scale)
            new_height = int(self.screen_size[1] * scale)
            self.last_frame = pygame.transform.scale(engine.scaled_surface, (new_width, new_height))

        self.active_type = menu_type
