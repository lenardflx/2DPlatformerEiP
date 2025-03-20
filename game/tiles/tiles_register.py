TILES_CLASSES = {}  # Registry for tiles types
def register_tile(name):
    """Decorator to register a tile class."""
    def wrapper(cls):
        TILES_CLASSES[name] = cls
        return cls
    return wrapper