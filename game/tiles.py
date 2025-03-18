import os.path
import pygame

BLOCK_TYPES = {}

def register_block(block_type):
    def wrapper(cls):
        BLOCK_TYPES[block_type] = cls
        return cls
    return wrapper

@register_block("block")
class Block:
    def __init__(self, texture, collision_type, metadata=None):
        self.texture = pygame.image.load(os.path.join("assets/tiles",texture)).convert_alpha()
        self.collision_type = collision_type
        self.metadata = metadata or {}

@register_block("pressure_plate")
class PressurePlate(Block):
    def on_touch(self, engine):
        engine.load_next_level()
