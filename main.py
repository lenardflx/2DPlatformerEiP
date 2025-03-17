from core.game_data import load_data
from core.engine import GameEngine

if __name__ == "__main__":
    try:
        load_data("data/game_data.json")
        game = GameEngine()
        game.run()
    except KeyboardInterrupt:
        print("Exiting game...")
    except Exception as e:
        print("An error occurred: " + str(e))
        raise