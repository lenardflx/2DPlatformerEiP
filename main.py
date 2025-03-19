import sys
import traceback
from core.game_data import load_data
from core.engine import GameEngine

if __name__ == "__main__":
    try:
        load_data("data/game_data.json")
        game = GameEngine()
        game.run()
    except KeyboardInterrupt:
        print("\n[INFO] Exiting game...")
        sys.exit(0)  # Clean exit without traceback
    except FileNotFoundError as e:
        print(f"[ERROR] Missing file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[CRITICAL] An unexpected error occurred: {e}")
        traceback.print_exc()  # Print full error traceback for debugging
        sys.exit(1)
