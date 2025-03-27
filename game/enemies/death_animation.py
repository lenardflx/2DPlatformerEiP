import pygame

_death_frames = None

def get_death_frames(tile_size=32, scale=1.0):
    global _death_frames
    if _death_frames is None:
        sheet = pygame.image.load("assets/characters/death_animation.png").convert_alpha()
        scaled_size = int(tile_size * scale)
        _death_frames = []
        frames_amount = sheet.get_width() // tile_size

        for col in range(frames_amount):
            x, y = col * tile_size, 0
            frame = sheet.subsurface((x, y, tile_size, tile_size))
            frame = pygame.transform.scale(frame, (scaled_size, scaled_size))
            _death_frames.append(frame)

    return _death_frames
