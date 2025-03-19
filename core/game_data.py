import json

game_data = {}

def load_data(json_path):
    """Loads game data from a JSON file."""
    global game_data
    with open(json_path) as f:
        game_data = json.load(f)

def get_game_data(key=None):
    """Returns the game data or a specific value from it."""
    if key:
        return game_data[key]
    return game_data