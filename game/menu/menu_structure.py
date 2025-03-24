import pygame

class Button:
    def __init__(self, name, sprites, pos, sound_manager, scale=2):
        self.name = name
        self.scale = scale
        self.sound_manager = sound_manager

        self.original_idle = sprites["idle"]
        self.original_hover = sprites.get("hover", [sprites["idle"]])

        self.idle_image = self.scale_image(self.original_idle)
        self.hover_images = [self.scale_image(frame) for frame in self.original_hover]
        self.hover_index = 0
        self.frame_timer = 0
        self.hovering = False

        self.rect = self.idle_image.get_rect(center=pos)

    def scale_image(self, img):
        if self.scale == 1:
            return img
        w = int(img.get_width() * self.scale)
        h = int(img.get_height() * self.scale)
        return pygame.transform.scale(img, (w, h))

    def update(self, mouse_pos):
        hovering = self.rect.collidepoint(mouse_pos)
        if hovering and not self.hovering:
            self.sound_manager.play_sfx("menu_hover")
        self.hovering = hovering
        if self.hovering:
            self.frame_timer += 1
            if self.frame_timer % 3 == 0:
                self.hover_index = min(self.hover_index + 1, len(self.hover_images) - 1)
        else:
            self.hover_index = 0
            self.frame_timer = 0

    def render(self, surface):
        # Draw button
        image = self.hover_images[self.hover_index] if self.hovering and self.hover_images else self.idle_image
        surface.blit(image, self.rect)

    def is_clicked(self, event, mouse_pos):
        is_clicked =  (
            event.type == pygame.MOUSEBUTTONDOWN and
            event.button == 1 and
            self.rect.collidepoint(mouse_pos)
        )
        if is_clicked:
            self.sound_manager.play_sfx("button_click")
        return is_clicked


class MenuPage:
    def __init__(self, font_manager, sound_manager):
        self.buttons = []
        self.font_manager = font_manager
        self.sound_manager = sound_manager

    def add_button(self, button):
        self.buttons.append(button)

    def update(self, mouse_pos):
        for button in self.buttons:
            button.update(mouse_pos)

    def render(self, surface):
        for button in self.buttons:
            button.render(surface)

    def handle_event(self, event, engine, mouse_pos):
        pass
