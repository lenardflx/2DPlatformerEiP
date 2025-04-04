import pygame

class Camera:
    def __init__(self, width, height, level_width, level_height):
        """Initializes the camera with screen size and level boundaries."""
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.level_width = level_width
        self.level_height = level_height

    def follow(self, target, smoothing=0.1):
        """Smoothly follows the target (e.g., player) using linear interpolation."""
        target_x = target.rect.centerx - self.width // 2
        target_y = target.rect.centery - self.height // 2

        # Apply smoothing
        self.camera.x += int((target_x - self.camera.x) * smoothing)
        self.camera.y += int((target_y - self.camera.y) * smoothing)

        # Clamp the camera to the level bounds
        self.camera.x = max(0, min(self.camera.x, self.level_width - self.width))
        self.camera.y = max(0, min(self.camera.y, self.level_height - self.height))

    def apply(self, target, speed=1):
        """Adjusts object position based on the camera's position."""
        if isinstance(target, pygame.Rect):
            return target.move(-self.camera.x * speed, -self.camera.y)
        elif hasattr(target, "render_rect"):
            return target.render_rect.move(-self.camera.x * speed, -self.camera.y)
        elif hasattr(target, "rect"):
            return target.rect.move(-self.camera.x * speed, -self.camera.y)
        return target

    def get_viewport(self):
        """Returns the camera's viewport position and size."""
        return self.camera.x, self.camera.y, self.width, self.height

    def is_visible(self, x, y, w, h):
        """Checks if an object is within the camera's view."""
        viewport_rect = pygame.Rect(self.camera.x, self.camera.y, self.width, self.height)
        object_rect = pygame.Rect(x, y, w, h)
        return viewport_rect.colliderect(object_rect)
