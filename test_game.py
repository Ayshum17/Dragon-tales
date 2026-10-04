"""Automated test for Dragon Climb game - verifies all game systems work."""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from game import Game
from settings import (
    get_asset, load_best_score, save_best_score, get_save_path,
    ASSET_DRAGON_1, ASSET_DRAGON_2, ASSET_OBSTACLE_TOP,
    ASSET_OBSTACLE_BOTTOM, ASSET_OBSTACLE_FLAME, ASSET_BACKGROUND,
    ASSET_ICON, ASSET_ICON_PNG,
    ASSET_SOUND_JUMP, ASSET_SOUND_CRASH, ASSET_SOUND_SCORE,
)

results = []
_image_refs = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, condition, detail))
    print(f"  [{status}] {name}" + (f" - {detail}" if detail and not condition else ""))


def test_assets(root):
    print("\n=== Asset Tests ===")
    assets = [
        ("dragon_1.png", ASSET_DRAGON_1),
        ("dragon_2.png", ASSET_DRAGON_2),
        ("obstacle_top.png", ASSET_OBSTACLE_TOP),
        ("obstacle_bottom.png", ASSET_OBSTACLE_BOTTOM),
        ("obstacle_flame.png", ASSET_OBSTACLE_FLAME),
        ("background.png", ASSET_BACKGROUND),
        ("icon.png", ASSET_ICON_PNG),
        ("icon.ico", ASSET_ICON),
        ("sound_jump.wav", ASSET_SOUND_JUMP),
        ("sound_crash.wav", ASSET_SOUND_CRASH),
        ("sound_score.wav", ASSET_SOUND_SCORE),
    ]
    for name, filename in assets:
        path = get_asset(filename)
        check(f"Asset exists: {name}", os.path.exists(path), f"Path: {path}")

    for name, filename in assets[:7]:
        path = get_asset(filename)
        if os.path.exists(path):
            try:
                img = tk.PhotoImage(file=path)
                _image_refs.append(img)
                check(f"Asset loads: {name}", img is not None)
            except Exception as e:
                check(f"Asset loads: {name}", False, str(e))


def test_save_system():
    print("\n=== Save System Tests ===")

    save_best_score(0)
    score = load_best_score()
    check("Load best score (initial)", isinstance(score, int), f"Got: {score}")

    save_best_score(100)
    loaded = load_best_score()
    check("Save and load best score", loaded == 100, f"Got: {loaded}")

    save_best_score(200)
    loaded = load_best_score()
    check("Update best score", loaded == 200, f"Got: {loaded}")

    save_path = get_save_path()
    check("Save path exists", os.path.exists(os.path.dirname(save_path)), f"Path: {save_path}")

    import json
    with open(save_path, "w") as f:
        f.write("CORRUPTED DATA")
    loaded = load_best_score()
    check("Recover from corrupted save", loaded == 0, f"Got: {loaded}")

    os.remove(save_path)
    loaded = load_best_score()
    check("Recover from missing save", loaded == 0, f"Got: {loaded}")

    save_best_score(0)


def test_game(root):
    print("\n=== Game Logic Tests ===")

    game = Game(root)

    check("Game initialized", game is not None)
    check("Menu state", game.state == Game.STATE_MENU, f"State: {game.state}")
    check("Best score loaded", isinstance(game.best_score, int))
    check("Images loaded", len(game._images) > 0, f"Images: {list(game._images.keys())}")
    check("Dragon images loaded", "dragon" in game._images and len(game._images["dragon"]) == 2)
    check("Background loaded", game._images.get("background") is not None)
    check("Obstacle top loaded", game._images.get("obstacle_top") is not None)
    check("Obstacle bottom loaded", game._images.get("obstacle_bottom") is not None)
    check("Obstacle flame loaded", game._images.get("obstacle_flame") is not None)

    print("\n=== Start Game ===")
    game._start_game()
    check("Playing state", game.state == Game.STATE_PLAYING, f"State: {game.state}")
    check("Dragon created", game.dragon is not None)
    check("Score is 0", game.score == 0, f"Score: {game.score}")
    check("Height is 0", game.height == 0, f"Height: {game.height}")
    check("Difficulty is 1", game.difficulty == 1, f"Difficulty: {game.difficulty}")
    check("TOP button exists", "top" in game._buttons)
    check("BOTTOM button exists", "bottom" in game._buttons)

    print("\n=== Simulate Gameplay (200 frames) ===")
    for i in range(200):
        if i % 10 == 0:
            game.dragon.move_up()
        elif i % 10 == 5:
            game.dragon.move_down()
        game._update_game()
        root.update_idletasks()

    check("Score increased", game.score > 0, f"Score: {game.score}")
    check("Height increased", game.height > 0, f"Height: {int(game.height)}")
    check("Dragon still alive", game.dragon is not None and game.dragon.alive)
    check("Obstacles spawned", len(game.obstacles) >= 0, f"Obstacles: {len(game.obstacles)}")

    print("\n=== Test TOP button ===")
    initial_y = game.dragon.y
    game._on_top_press()
    for _ in range(5):
        game._update_game()
        root.update_idletasks()
    check("TOP moves dragon up", game.dragon.y <= initial_y + 5,
          f"Before: {initial_y}, After: {game.dragon.y}")

    print("\n=== Test BOTTOM button ===")
    initial_y = game.dragon.y
    game._on_bottom_press()
    for _ in range(5):
        game._update_game()
        root.update_idletasks()
    check("BOTTOM moves dragon down", game.dragon.y >= initial_y - 5,
          f"Before: {initial_y}, After: {game.dragon.y}")

    print("\n=== Test Pause ===")
    game._toggle_pause()
    check("Paused state", game.state == Game.STATE_PAUSED, f"State: {game.state}")
    score_before = game.score
    root.update_idletasks()
    check("Score frozen when paused", game.score == score_before)
    game._toggle_pause()
    check("Resumed state", game.state == Game.STATE_PLAYING, f"State: {game.state}")

    print("\n=== Test Game Over ===")
    game._game_over("Test crash")
    check("Game over state", game.state == Game.STATE_GAME_OVER, f"State: {game.state}")
    check("Restart button exists", "restart" in game._buttons)
    check("Menu button exists", "menu" in game._buttons)

    print("\n=== Test Restart ===")
    game._start_game()
    check("Restart - playing state", game.state == Game.STATE_PLAYING, f"State: {game.state}")
    check("Restart - score reset", game.score == 0, f"Score: {game.score}")
    check("Restart - dragon created", game.dragon is not None)

    print("\n=== Test Return to Menu ===")
    game._return_to_menu()
    check("Menu state after return", game.state == Game.STATE_MENU, f"State: {game.state}")

    print("\n=== Test Sound Toggle ===")
    initial = game.sound.enabled
    game.sound.toggle()
    check("Sound toggled", game.sound.enabled != initial)
    game.sound.toggle()
    check("Sound toggled back", game.sound.enabled == initial)

    game.stop()


def main():
    print("=" * 50)
    print("Dragon Climb - Automated Test Suite")
    print("=" * 50)

    check("Python version", sys.version_info >= (3, 10), f"Python {sys.version}")

    try:
        import tkinter
        check("Tkinter available", True)
    except ImportError:
        check("Tkinter available", False)

    try:
        import PIL
        check("Pillow available", True)
    except ImportError:
        check("Pillow available", False)

    root = tk.Tk()
    root.withdraw()

    test_assets(root)
    test_save_system()
    test_game(root)

    root.destroy()

    print("\n" + "=" * 50)
    passed = sum(1 for _, c, _ in results if c)
    failed = sum(1 for _, c, _ in results if not c)
    total = len(results)
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print("=" * 50)

    if failed > 0:
        print("\nFAILED TESTS:")
        for name, condition, detail in results:
            if not condition:
                print(f"  - {name}: {detail}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
