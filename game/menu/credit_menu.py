import pygame
from game.menu.menu_structure import MenuPage
from game.menu.menu_state import MenuState

class CreditMenu(MenuPage):
    def __init__(self, screen_size, font_manager, sound_manager, menu):
        super().__init__(font_manager, sound_manager)
        self.engine = None
        self.screen_width, self.screen_height = screen_size
        self.scroll_y = self.screen_height  # Start offscreen at bottom
        self.scroll_speed = 1.2

        self.menu = menu
        self.done = False
        self.allow_skip = False  # Delay skip to avoid instant trigger

        self.skip_delay_frames = 15
        self.frame_counter = 0

        self.lines = [
            "YOU WON THE GAME!",
            "",
            "After disabling the final protocol,",
            "humanity begins to rebuild what was lost.",
            "NEUROS has been silenced,",
            "but a new threat to humanity will soon emerge.",
            "",
            "",
            "=== CREDITS ===",
            "Developers:",
            "Lenard Felix",
            "Christopher Ionescu",
            "David Sieper",
            "Philipp Seng",
            "",
            "Design:",
            "Lenard Felix",
            "David Sieper",
            "",
            "Music:",
            "Lenard Felix",
            "",
            "Thank you for playing",
            "<Protocol: Disconnect>.",
        ]

        self.line_height = 40
        self.total_height = len(self.lines) * self.line_height
        self.final_scroll_y = -self.total_height - 100  # Off screen

    def update(self, mouse_pos):
        self.frame_counter += 1
        if self.frame_counter > self.skip_delay_frames:
            self.allow_skip = True

        if not self.done:
            self.scroll_y -= self.scroll_speed
            if self.scroll_y < self.final_scroll_y:
                self.end_credits()

        if self.allow_skip:
            keys = pygame.key.get_pressed()
            mouse = pygame.mouse.get_pressed()
            if any(keys) or any(mouse):
                self.end_credits()

    def render(self, surface):
        surface.fill((10, 10, 10))
        for i, line in enumerate(self.lines):
            y = self.scroll_y + i * self.line_height
            if -self.line_height < y < self.screen_height + self.line_height:
                color = (255, 255, 255)
                if "===" in line:
                    color = (255, 215, 0)
                elif "<" in line:
                    color = (100, 200, 255)

                self.font_manager.render(
                    surface,
                    text=line,
                    position=(self.screen_width // 2, y),
                    size=30,
                    color=color,
                    align_center=True
                )

    def handle_event(self, event, engine, mouse_pos):
        self.engine = engine

    def end_credits(self):
        self.done = True
        self.menu.open_menu(MenuState.MAIN, self.engine)
