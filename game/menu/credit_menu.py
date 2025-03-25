import pygame
from game.menu.menu_structure import MenuPage
from game.menu.menu_state import MenuState

class CreditMenu(MenuPage):
    def __init__(self, screen_size, font_manager, sound_manager, menu):
        super().__init__(font_manager, sound_manager)
        self.screen_width, self.screen_height = screen_size
        self.scroll_y = self.screen_height  # Start from bottom
        self.scroll_speed = 1.2  # Adjust for speed
        self.credits_done = False

        self.skip_hold_frames = 0
        self.skip_threshold = 3
        self.menu = menu

        # Setup text blocks
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
        self.final_scroll_y = -self.total_height - 100  # Go off-screen before ending

    def update(self, mouse_pos):
        if not self.credits_done:
            self.scroll_y -= self.scroll_speed
            if self.scroll_y < self.final_scroll_y:
                self.credits_done = True

        # Skip logic
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        if any(keys) or mouse[0]:
            self.skip_hold_frames += 1
        else:
            self.skip_hold_frames = 0

        if self.skip_hold_frames >= self.skip_threshold or self.credits_done:
            self.end_credits()

    def render(self, surface):
        surface.fill((10, 10, 10))

        for i, line in enumerate(self.lines):
            y = self.scroll_y + i * self.line_height
            if -self.line_height < y < self.screen_height + self.line_height:
                color = (255, 255, 255) if ("===" not in line and "<" not in line) else (255, 215, 0)
                self.font_manager.render(
                    surface,
                    text=line,
                    position=(self.screen_width // 2, y),
                    size=30,
                    color=color,
                    align_center=True
                )

    def handle_event(self, event, engine, mouse_pos):
        # Skip logic handled in update()
        pass

    def end_credits(self):
        self.credits_done = True
        self.menu.open_menu(MenuState.MAIN, self.menu.engine)
