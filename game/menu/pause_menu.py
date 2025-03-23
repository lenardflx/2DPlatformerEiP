import pygame

from game.menu.menu_structure import MenuPage, Button
from game.menu.menu_state import MenuState

class PauseMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, sound_manager):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.cx, self.cy = screen_size[0] // 2, screen_size[1] // 2

        spacing = 80
        button_names = ["resume", "retry", "options", "menu"]
        for i, name in enumerate(button_names):
            y = self.cy - spacing + i * spacing
            self.add_button(Button(name, button_images[name], (self.cx, y), sound_manager))

    def render(self, surface):
        self.font_manager.render(
            text="Paused",
            surface=surface,
            position=(self.cx, 80),
            size=44,
            color=(255, 255, 255),
            align_center=True
        )
        super().render(surface)

    def handle_event(self, event, engine, mouse_pos):
        for button in self.buttons:
            if button.is_clicked(event, mouse_pos):
                if button.name == "resume":
                    engine.menu.close_menu(engine)
                elif button.name == "retry":
                    engine.load_level(engine.current_level)
                    engine.menu.close_menu(engine)
                elif button.name == "menu":
                    engine.menu.set_active_page(MenuState.MAIN)
                elif button.name == "options":
                    engine.menu.set_active_page(MenuState.SETTINGS)
