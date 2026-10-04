"""Dragon Climb - Entry Point.

Run the game:
    python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from game import Game


def main():
    root = tk.Tk()
    root.title("Dragon Climb")

    game = Game(root)

    def on_closing():
        game.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()