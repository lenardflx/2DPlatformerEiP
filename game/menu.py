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
        self.last_frame = None

        self.buttons = {
            "start": {
                "image": pygame.image.load(os.path.join("assets/menu", menu_data["start_button"])).convert_alpha(),
                "rect": None,
                "hovered": False,
                "scale_factor": 1.0
            },
            "quit": {
                "image": pygame.image.load(os.path.join("assets/menu", menu_data["quit_button"])).convert_alpha(),
                "rect": None,
                "hovered": False,
                "scale_factor": 1.0
            }
        }

        for key in self.buttons:
            self.buttons[key]["rect"] = self.buttons[key]["image"].get_rect()

    def handle_events(self, engine):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.is_running = False
            elif event.type == pygame.VIDEORESIZE:
                self.update_layout(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for key, button in self.buttons.items():
                    if button["rect"].collidepoint(event.pos):
                        if key == "start":
                            engine.is_menu = False
                        elif key == "quit":
                            engine.is_running = False

        for key, button in self.buttons.items():
            button["hovered"] = button["rect"].collidepoint(mouse_pos)

    def update_layout(self, screen_width, screen_height):
        button_spacing = 80
        self.buttons["start"]["rect"].center = (screen_width // 2, screen_height // 2 - button_spacing)
        self.buttons["quit"]["rect"].center = (screen_width // 2, screen_height // 2 - (button_spacing // 3))

    def render(self, screen):
        if self.active_type == MenuOptions.START:
            screen.fill((0, 0, 255))
        else:
            if self.last_frame:
                screen.blit(self.last_frame, (0, 0))

            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            if self.active_type == MenuOptions.PAUSE:
                overlay.fill((128, 128, 128, 128))
            elif self.active_type == MenuOptions.DEATH:
                overlay.fill((255, 0, 0, 128))

            screen.blit(overlay, (0, 0))

        lerp_speed = 0.1

        for key, button in self.buttons.items():
            target_scale = 1.2 if button["hovered"] else 1.0
            button["scale_factor"] += (target_scale - button["scale_factor"]) * lerp_speed

            base_size = button["image"].get_size()
            scaled_width = int(base_size[0] * button["scale_factor"])
            scaled_height = int(base_size[1] * button["scale_factor"])

            scaled_image = pygame.transform.scale(button["image"], (scaled_width, scaled_height))
            scaled_rect = scaled_image.get_rect(center=button["rect"].center)

            screen.blit(scaled_image, scaled_rect)

    def open_menu(self, menu_type, engine):
        self.active_type = menu_type
        self.last_frame = engine.screen.copy()
        for button in self.buttons.values():
            button["scale_factor"] = 1.0
        engine.is_menu = True
