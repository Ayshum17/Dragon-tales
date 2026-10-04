"""Game settings, constants, and resource path helpers for Dragon Climb."""

import os
import sys
import json

# ─── Window ───
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Dragon Climb"
FPS = 60

# ─── Colors (hex strings for Tkinter) ───
COLOR_BG = "#1E1E3C"
COLOR_SKY = "#1E3264"
COLOR_WHITE = "#FFFFFF"
COLOR_BLACK = "#000000"
COLOR_RED = "#DC3C3C"
COLOR_GREEN = "#3CC850"
COLOR_BLUE = "#3C78DC"
COLOR_YELLOW = "#FFDC3C"
COLOR_ORANGE = "#FF8C1E"
COLOR_GRAY = "#64646E"
COLOR_DARK = "#0F0F19"
COLOR_PANEL = "#192337"
COLOR_BUTTON_TOP = "#3CB464"
COLOR_BUTTON_BOTTOM = "#3C78C8"
COLOR_BUTTON_HOVER = "#50C878"

# ─── Game Parameters ───
DRAGON_SIZE = 60
DRAGON_X = 120
DRAGON_START_Y = WINDOW_HEIGHT // 2
DRAGON_SPEED_UP = 6
DRAGON_SPEED_DOWN = 4
DRAGON_GRAVITY = 0.3
DRAGON_MAX_SPEED = 10

OBSTACLE_WIDTH = 70
OBSTACLE_MIN_GAP = 150
OBSTACLE_MAX_GAP = 250
OBSTACLE_BASE_SPEED = 3
OBSTACLE_SPAWN_INTERVAL = 90

FLAME_SIZE = 50
FLAME_BASE_SPEED = 4

SCORE_PER_FRAME = 1
HEIGHT_PER_FRAME = 0.5
DIFFICULTY_INTERVAL = 500

# ─── Resource Path ───

def is_frozen():
    """Return True if running inside a PyInstaller bundle."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_resource_path(relative_path):
    """
    Get the absolute path to a resource file.

    Works both in development mode (python main.py) and in a PyInstaller
    bundle (DragonClimb.exe) by accounting for sys._MEIPASS.
    """
    if is_frozen():
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def get_assets_dir():
    """Return the absolute path to the assets directory."""
    return get_resource_path("assets")


def get_asset(filename):
    """Return the full path to an asset file inside assets/."""
    return get_resource_path(os.path.join("assets", filename))


# ─── Save Data Path ───

def get_save_dir():
    """
    Return a writable directory for save data.

    In a PyInstaller bundle, the bundle directory is read-only, so we use
    the user's AppData directory on Windows or a local .dragonclimb folder.
    """
    if is_frozen():
        app_name = "DragonClimb"
        if sys.platform == "win32":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            base = os.path.expanduser("~")
        save_dir = os.path.join(base, app_name)
    else:
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")

    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def get_save_path(filename="best_score.json"):
    """Return the full path to a save file."""
    return os.path.join(get_save_dir(), filename)


def load_best_score():
    """
    Load the best score from the save file.

    Returns 0 if the file is missing or corrupted.
    """
    path = get_save_path()
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return int(data.get("best_score", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError, KeyError):
        return 0


def save_best_score(score):
    """
    Save the best score to the save file.

    Creates the directory if it does not exist. Silently ignores write errors.
    """
    path = get_save_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump({"best_score": int(score)}, f, indent=2)
    except (OSError, IOError, TypeError):
        pass


# ─── Asset Filenames ───

ASSET_DRAGON_1 = "dragon_1.png"
ASSET_DRAGON_2 = "dragon_2.png"
ASSET_DRAGON = "dragon.png"
ASSET_OBSTACLE_TOP = "obstacle_top.png"
ASSET_OBSTACLE_BOTTOM = "obstacle_bottom.png"
ASSET_OBSTACLE_FLAME = "obstacle.png"
ASSET_BACKGROUND = "background.png"
ASSET_ICON = "dragon_climb.ico"
ASSET_ICON_PNG = "dragon_climb_icon.png"
ASSET_SOUND_JUMP = "sound_jump.wav"
ASSET_SOUND_CRASH = "sound_crash.wav"
ASSET_SOUND_SCORE = "sound_score.wav"