import pygame
from game.menu.menu_structure import MenuPage, Button
from game.menu.menu_state import MenuState

class WinMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, sound_manager):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.cx, self.cy = screen_size[0] // 2, screen_size[1] // 2
        self.button_images = button_images

        # Background color
        self.background_color = (20, 20, 40)  # Dark blue for a victory feel

        # Title
        self.title = "MISSION COMPLETE"
        self.title_color = (255, 215, 0)

        # Stars setup
        self.star_count = 3
        self.star_size = 60
        self.star_spacing = 80
        self.star_y = self.cy - 50
        self.star_animation_time = 0
        self.star_scale = 1.0

        # Buttons
        spacing = 80
        options = [
            ("resume", "Resume", self.cy + spacing),
            ("menu", "Menu", self.cy + 2 * spacing)
        ]
        for name, display_name, y in options:
            self.add_button(Button(name, button_images[name], (self.cx, y), sound_manager))

    def update(self, mouse_pos):
        """Update star animation"""
        self.star_animation_time += 0.05  # Speed of animation
        # Create a pulsing effect for stars
        self.star_scale = 1.0 + 0.1 * abs(pygame.math.Vector2().rotate(self.star_animation_time * 360).y)
        super().update(mouse_pos)

    def render(self, surface):
        """Render the win screen"""
        surface.fill(self.background_color)

        # Draw a subtle gradient background
        for i in range(self.screen_size[1]):
            color = (
                self.background_color[0],
                self.background_color[1],
                int(self.background_color[2] + (i / self.screen_size[1]) * 20)
            )
            pygame.draw.line(surface, color, (0, i), (self.screen_size[0], i))

        # Title
        self.font_manager.render(
            surface=surface,
            text=self.title,
            position=(self.cx, 100),
            size=48,
            color=self.title_color,
            align_center=True
        )

        # Render buttons
        super().render(surface)

    def handle_event(self, event, engine, mouse_pos):
        """Handle button clicks"""
        for button in self.buttons:
            if button.is_clicked(event, mouse_pos):
                if button.name == "resume":
                    engine.is_playing = True
                    engine.menu.close_menu(engine)
                elif button.name == "menu":
                    engine.is_playing = False
                    engine.menu.open_menu(MenuState.MAIN, engine)