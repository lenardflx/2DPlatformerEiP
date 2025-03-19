ENEMY_CLASSES = {}  # Registry for enemy types

def register_enemy(name):
    """Decorator to register an enemy class."""
    def wrapper(cls):
        ENEMY_CLASSES[name] = cls
        return cls
    return wrapper