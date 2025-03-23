from game.menu.menu_structure import MenuPage, Button
from game.menu.menu_state import MenuState

class DeathMenu(MenuPage):
    def __init__(self, screen_size, button_images, font_manager, sound_manager):
        super().__init__(font_manager, sound_manager)
        self.screen_size = screen_size
        self.cx, self.cy = screen_size[0] // 2, screen_size[1] // 2
        self.button_images = button_images

        spacing = 80
        options = ["retry", "menu"]
        for i, name in enumerate(options):
            y = self.cy + i * spacing
            self.add_button(Button(name, button_images[name], (self.cx, y), sound_manager))

        self.title = "YOU DIED"

    def render(self, surface):
        self.font_manager.render(
            surface=surface,
            text=self.title,
            position=(self.cx, 100),
            size=48,
            color=(255, 80, 80),
            align_center=True
        )
        super().render(surface)

    def handle_event(self, event, engine, mouse_pos):
        for button in self.buttons:
            if button.is_clicked(event, mouse_pos):
                if button.name == "retry":
                    engine.load_level(engine.current_level)
                    engine.is_playing = True
                    engine.menu.close_menu(engine)
                elif button.name == "menu":
                    engine.is_playing = False
                    engine.menu.open_menu(MenuState.MAIN, engine)
