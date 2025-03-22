import json
import os
import pygame

class MenuState:
    """Menu state enumeration for different screens."""
    NONE = 0
    MAIN = 1
    PAUSE = 2
    DEATH = 3
    SETTINGS = 4
    LEVELS = 5

class Menu:
    def __init__(self, screen_size, controls):
        """Initializes the menu system and loads UI assets."""
        pygame.font.init()

        # Load settings
        with open("assets/menu/menu.json") as f:
            menu_data = json.load(f)

        self.active_type = MenuState.MAIN
        self.last_frame = None
        self.menu_history = []
        self.screen_size = screen_size

        # Load background image
        # self.background = pygame.image.load("assets/menu/background.png").convert()

        # Load button images
        self.button_image = pygame.image.load(
            os.path.join("assets/menu", menu_data["button_image"])).convert_alpha()
        self.button_hover_image = pygame.image.load(
            os.path.join("assets/menu", menu_data["button_hover_image"])).convert_alpha()

        # Load font
        self.font = pygame.font.Font("assets/font/font.otf", 20)

        # Define button layouts
        self.menu_layouts = {
            MenuState.MAIN: ["start", "resume", "levels", "settings", "exit"],
            MenuState.PAUSE: ["resume", "retry", "settings", "main_menu"],
            MenuState.DEATH: ["retry", "main_menu"],
            MenuState.SETTINGS: ["back"],
            MenuState.LEVELS: ["back"]
        }

        # Button storage
        self.buttons = {key: {"rect": pygame.Rect(0, 0, self.button_image.get_width(), self.button_image.get_height()),
                              "hovered": False, "text": key.replace("_", " ").title()}
                        for key in set(sum(self.menu_layouts.values(), []))}

        # Volume Slider
        self.volume = pygame.mixer.music.get_volume()
        self.slider_rect = pygame.Rect(300, 500, 200, 20)
        self.dragging_slider = False

        # Key Rebinding
        self.controls = controls
        self.waiting_for_key = None  # If set, waiting for a key press

    def handle_event(self, event, engine):
        """Handles menu events, including key rebindings & volume control."""
        mouse_x, mouse_y = self.scale_mouse_position(engine)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.active_type == MenuState.SETTINGS:
                    # Check if volume slider is clicked
                    if self.slider_rect.collidepoint(mouse_x, mouse_y):
                        self.dragging_slider = True
                        self.set_volume(mouse_x)

                    # Check key bindings
                    for action, (rect1, rect2) in self.get_key_binding_rects().items():
                        if rect1.collidepoint(mouse_x, mouse_y):
                            self.waiting_for_key = (action, 0)  # First key slot
                            return
                        if rect2.collidepoint(mouse_x, mouse_y):
                            self.waiting_for_key = (action, 1)  # Second key slot
                            return

                # Check if a button was clicked
                for key, button in self.buttons.items():
                    if button["rect"].collidepoint((mouse_x, mouse_y)):
                        self.handle_button_action(key, engine)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = False

        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            self.set_volume(mouse_x)

        elif event.type == pygame.KEYDOWN and self.waiting_for_key:
            # If waiting for a key to rebind
            self.controls.bind_key(self.waiting_for_key, event.key)
            self.waiting_for_key = None  # Stop waiting

        # Hover detection
        for key, button in self.buttons.items():
            button["hovered"] = button["rect"].collidepoint((mouse_x, mouse_y))

    def set_volume(self, mouse_x):
        """Adjusts volume based on slider position."""
        volume = max(0, min(1, (mouse_x - self.slider_rect.x) / self.slider_rect.width))
        pygame.mixer.music.set_volume(volume)
        self.volume = volume

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

    def handle_button_action(self, key, engine):
        """Handles button press logic."""
        if key == "start":
            engine.start_game()
            self.active_type = MenuState.NONE
        elif key == "resume":
            engine.is_playing = True
            self.active_type = MenuState.NONE
        elif key == "retry":
            engine.load_level(engine.current_level)
            engine.is_playing = True
            self.active_type = MenuState.NONE
        elif key == "main_menu":
            self.active_type = MenuState.MAIN
            engine.load_level(0)
            engine.is_playing = False
            self.last_frame = None
        elif key == "settings":
            self.open_menu(MenuState.SETTINGS, engine)
        elif key == "levels":
            self.open_menu(MenuState.LEVELS, engine)
        elif key == "exit":
            pygame.quit()
            exit()
        elif key == "back":
            if self.menu_history:
                self.active_type = self.menu_history.pop()
            else:
                self.active_type = MenuState.MAIN

    def render(self, screen):
        """Renders the menu and UI."""
        if self.active_type == MenuState.NONE:
            return
        if self.active_type == MenuState.MAIN:
            screen.fill((0, 0, 255)) # TODO: Replace with background image

        if self.last_frame:
            screen.blit(self.last_frame, (0, 0))

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((128, 128, 128, 128))  # Semi-transparent overlay
        screen.blit(overlay, (0, 0))

        # Render buttons
        screen_width, screen_height = screen.get_size()
        if self.active_type == MenuState.SETTINGS:
            self.render_settings(screen)
            return
        button_spacing = 80
        menu_buttons = self.menu_layouts.get(self.active_type, [])

        for i, key in enumerate(menu_buttons):
            button = self.buttons[key]
            image = self.button_hover_image if button["hovered"] else self.button_image

            rect = image.get_rect()
            rect.center = (screen_width // 2, screen_height // 2 + i * button_spacing - len(menu_buttons) * 25)
            button["rect"] = rect

            screen.blit(image, rect)
            self.render_text(screen, button["text"], rect.centerx, rect.centery)

    def render_settings(self, screen):
        """Renders the settings menu."""
        screen_width = screen.get_width()
        self.render_text(screen, "Settings", screen_width // 2, 50, size=40)

        # Key Bindings
        y_start = 150
        key_binding_rects = self.get_key_binding_rects()
        for action, rects in key_binding_rects.items():
            action_text = action.replace("_", " ").title()
            keys = [
                pygame.key.name(key) if key is not None else "UNBOUND"
                for key in self.controls.controls.get(action, [None, None])
            ]

            self.render_text(screen, action_text, 200, y_start, size=24)

            for i, rect in enumerate(rects):
                pygame.draw.rect(screen, (50, 50, 50) if self.waiting_for_key != (action, i) else (200, 50, 50), rect, border_radius=5)
                self.render_text(screen, keys[i], rect.centerx, rect.centery, size=24)
            y_start += 50

        # Volume Slider
        pygame.draw.rect(screen, (255, 255, 255), self.slider_rect, border_radius=10)
        pygame.draw.circle(screen, (0, 255, 0), (int(self.slider_rect.x + self.volume * self.slider_rect.width), self.slider_rect.centery), 10)
        self.render_text(screen, f"Volume: {int(self.volume * 100)}%", self.slider_rect.centerx, self.slider_rect.top - 30)

    def get_key_binding_rects(self):
        """Returns rects for both key bindings of each action."""
        return {
            action: (
                pygame.Rect(400, 150 + i * 50, 100, 30),  # First key binding box
                pygame.Rect(520, 150 + i * 50, 100, 30)  # Second key binding box
            )
            for i, action in enumerate(self.controls.controls)
        }

    @staticmethod
    def render_text(screen, text, x, y, size=30, color=(255, 255, 255)):
        """Renders text on the menu."""
        font = pygame.font.Font("assets/font/font.otf", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    def open_menu(self, menu_type, engine):
        """Opens a new menu and captures the game frame correctly after resizing."""
        if engine.is_playing:
            # Get the correct scaled game frame before opening the menu
            self.last_frame = pygame.transform.scale(engine.scaled_surface, engine.native_size)
        else:
            self.menu_history.append(self.active_type)

        engine.is_playing = False
        self.active_type = menu_type

    def close_menu(self, engine):
        """Closes the current menu and resumes the game."""
        engine.is_playing = True
        self.active_type = MenuState.NONE
        self.last_frame = None

    def toggle_menu(self, open_type, engine):
        """Toggles the menu state."""
        if self.active_type == MenuState.NONE:
            self.open_menu(open_type, engine)
        else:
            self.close_menu(engine)