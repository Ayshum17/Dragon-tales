"""Dragon Climb - a vertical climbing dodge game built with Tkinter."""

import random
import math
import time
import threading

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    raise RuntimeError("Tkinter is required to run Dragon Climb.")

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS,
    COLOR_BG, COLOR_WHITE, COLOR_BLACK, COLOR_RED, COLOR_GREEN,
    COLOR_BLUE, COLOR_YELLOW, COLOR_ORANGE, COLOR_GRAY, COLOR_DARK,
    COLOR_PANEL, COLOR_BUTTON_TOP, COLOR_BUTTON_BOTTOM, COLOR_BUTTON_HOVER,
    DRAGON_SIZE, DRAGON_X, DRAGON_START_Y,
    DRAGON_SPEED_UP, DRAGON_SPEED_DOWN, DRAGON_GRAVITY, DRAGON_MAX_SPEED,
    OBSTACLE_WIDTH, OBSTACLE_MIN_GAP, OBSTACLE_MAX_GAP,
    OBSTACLE_BASE_SPEED, OBSTACLE_SPAWN_INTERVAL,
    FLAME_SIZE, FLAME_BASE_SPEED,
    SCORE_PER_FRAME, HEIGHT_PER_FRAME, DIFFICULTY_INTERVAL,
    get_asset, get_resource_path, is_frozen,
    load_best_score, save_best_score,
    ASSET_DRAGON_1, ASSET_DRAGON_2, ASSET_OBSTACLE_TOP,
    ASSET_OBSTACLE_BOTTOM, ASSET_OBSTACLE_FLAME, ASSET_BACKGROUND,
    ASSET_ICON, ASSET_ICON_PNG,
    ASSET_SOUND_JUMP, ASSET_SOUND_CRASH, ASSET_SOUND_SCORE,
)


class SoundManager:
    """Manage sound playback with graceful fallback when sounds are unavailable."""

    def __init__(self):
        self.enabled = True
        self._channels = {}
        try:
            import winsound
            self._winsound = winsound
            self._use_winsound = True
        except ImportError:
            self._winsound = None
            self._use_winsound = False

        self._sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        sounds = {
            "jump": ASSET_SOUND_JUMP,
            "crash": ASSET_SOUND_CRASH,
            "score": ASSET_SOUND_SCORE,
        }
        for key, filename in sounds.items():
            path = get_asset(filename)
            try:
                if self._use_winsound:
                    import wave
                    with wave.open(path, "rb") as wf:
                        frames = wf.readframes(wf.getnframes())
                    self._sounds[key] = path
                else:
                    pass
            except Exception:
                self._sounds[key] = None

    def play(self, name):
        if not self.enabled:
            return
        path = self._sounds.get(name)
        if path is None:
            return
        try:
            if self._use_winsound:
                self._winsound.PlaySound(path, self._winsound.SND_ASYNC | self._winsound.SND_MEMORY)
        except Exception:
            pass

    def play_async(self, name):
        thread = threading.Thread(target=self.play, args=(name,), daemon=True)
        thread.start()

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled


class Dragon:
    """The player-controlled dragon."""

    def __init__(self, canvas, images):
        self.canvas = canvas
        self.images = images
        self.x = DRAGON_X
        self.y = DRAGON_START_Y
        self.velocity = 0
        self.frame = 0
        self.frame_timer = 0
        self.alive = True

        self.id = canvas.create_image(self.x, self.y, image=images[0], anchor=tk.CENTER)

    def move_up(self):
        if self.alive:
            self.velocity = -DRAGON_SPEED_UP

    def move_down(self):
        if self.alive:
            self.velocity = DRAGON_SPEED_DOWN

    def boost(self):
        if self.alive:
            self.velocity = -DRAGON_SPEED_UP * 1.2

    def update(self):
        if not self.alive:
            return

        self.velocity += DRAGON_GRAVITY
        self.velocity = max(-DRAGON_MAX_SPEED, min(DRAGON_MAX_SPEED, self.velocity))
        self.y += self.velocity

        if self.y < DRAGON_SIZE // 2:
            self.y = DRAGON_SIZE // 2
            self.velocity = 0
        if self.y > WINDOW_HEIGHT - DRAGON_SIZE // 2:
            self.y = WINDOW_HEIGHT - DRAGON_SIZE // 2
            self.velocity = 0

        self.frame_timer += 1
        if self.frame_timer >= 8:
            self.frame_timer = 0
            self.frame = 1 - self.frame

        self.canvas.itemconfig(self.id, image=self.images[self.frame])
        self.canvas.coords(self.id, self.x, self.y)

    def get_bbox(self):
        half = DRAGON_SIZE // 2 - 4
        return (self.x - half, self.y - half, self.x + half, self.y + half)

    def destroy(self):
        self.alive = False
        self.canvas.delete(self.id)


class Obstacle:
    """A rock wall obstacle (top or bottom)."""

    def __init__(self, canvas, image, x, y, speed, is_top):
        self.canvas = canvas
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed
        self.is_top = is_top
        self.passed = False

        self.id = canvas.create_image(self.x, self.y, image=image, anchor=tk.NW)

    def update(self):
        self.x -= self.speed
        self.canvas.coords(self.id, self.x, self.y)

    def get_bbox(self):
        return (self.x + 5, self.y + 5, self.x + OBSTACLE_WIDTH - 5, self.y + 195)

    def is_offscreen(self):
        return self.x + OBSTACLE_WIDTH < 0

    def destroy(self):
        self.canvas.delete(self.id)


class FlameObstacle:
    """A fireball obstacle that moves diagonally."""

    def __init__(self, canvas, image, x, y, speed):
        self.canvas = canvas
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed
        self.passed = False
        self.angle = random.uniform(-0.3, 0.3)

        self.id = canvas.create_image(self.x, self.y, image=image, anchor=tk.CENTER)

    def update(self):
        self.x -= self.speed
        self.y += self.speed * self.angle * 2
        self.canvas.coords(self.id, self.x, self.y)

    def get_bbox(self):
        half = FLAME_SIZE // 2 - 5
        return (self.x - half, self.y - half, self.x + half, self.y + half)

    def is_offscreen(self):
        return self.x + FLAME_SIZE < 0

    def destroy(self):
        self.canvas.delete(self.id)


def check_collision(bbox1, bbox2):
    """Check if two bounding boxes overlap."""
    return not (bbox1[2] < bbox2[0] or bbox1[0] > bbox2[2] or
                bbox1[3] < bbox2[1] or bbox1[1] > bbox2[3])


class Game:
    """Main game controller managing screens, state, and the game loop."""

    # Screen states
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_GAME_OVER = "game_over"

    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.resizable(False, False)

        self._set_window_icon()

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                                bg=COLOR_DARK, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.state = self.STATE_MENU
        self.sound = SoundManager()

        self._images = {}
        self._load_images()
        self._setup_background()

        self.dragon = None
        self.obstacles = []
        self.score = 0
        self.height = 0
        self.best_score = load_best_score()
        self.difficulty = 1
        self.spawn_timer = 0
        self.frame_count = 0
        self.game_over_reason = ""

        self._ui_elements = {}
        self._buttons = {}

        self._build_menu()

        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)

        self._key_up = False
        self._key_down = False

        self._running = True
        self._last_time = time.time()
        self._loop()

    def _set_window_icon(self):
        try:
            icon_path = get_asset(ASSET_ICON)
            if not is_frozen():
                img = tk.PhotoImage(file=get_asset(ASSET_ICON_PNG))
                self.root.iconphoto(True, img)
        except Exception:
            pass

    def _load_images(self):
        dragon_imgs = []
        for name in (ASSET_DRAGON_1, ASSET_DRAGON_2):
            try:
                img = tk.PhotoImage(file=get_asset(name))
            except Exception:
                img = self._fallback_dragon_image()
            dragon_imgs.append(img)
        self._images["dragon"] = dragon_imgs

        for key, name in [
            ("obstacle_top", ASSET_OBSTACLE_TOP),
            ("obstacle_bottom", ASSET_OBSTACLE_BOTTOM),
            ("obstacle_flame", ASSET_OBSTACLE_FLAME),
            ("background", ASSET_BACKGROUND),
        ]:
            try:
                self._images[key] = tk.PhotoImage(file=get_asset(name))
            except Exception:
                self._images[key] = None

    def _fallback_dragon_image(self):
        return None

    def _setup_background(self):
        bg = self._images.get("background")
        if bg:
            self._bg_id = self.canvas.create_image(0, 0, image=bg, anchor=tk.NW)
        else:
            self._bg_id = self.canvas.create_rectangle(
                0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill=COLOR_BG, outline="")

    # ─── Menu Screen ───

    def _build_menu(self):
        self._clear_ui()

        cx = WINDOW_WIDTH // 2

        self._ui_elements["title"] = self.canvas.create_text(
            cx, 150, text="DRAGON CLIMB", font=("Arial", 32, "bold"),
            fill=COLOR_YELLOW)

        self._ui_elements["subtitle"] = self.canvas.create_text(
            cx, 200, text="Climb as high as you can!", font=("Arial", 14),
            fill=COLOR_WHITE)

        if self.best_score > 0:
            self._ui_elements["best"] = self.canvas.create_text(
                cx, 250, text=f"Best Score: {self.best_score}",
                font=("Arial", 16, "bold"), fill=COLOR_ORANGE)

        self._ui_elements["instructions"] = self.canvas.create_text(
            cx, 320,
            text="Controls:\n"
                 "  TOP / Up Arrow / W  -  Move Up\n"
                 "  BOTTOM / Down Arrow / S  -  Move Down\n"
                 "  SPACE  -  Boost\n"
                 "  P  -  Pause\n"
                 "  M  -  Toggle Sound",
            font=("Arial", 12), fill=COLOR_WHITE, justify=tk.LEFT)

        self._add_button("start", cx - 80, 480, 160, 50,
                         "START GAME", COLOR_GREEN, self._start_game)

        self._ui_elements["footer"] = self.canvas.create_text(
            cx, WINDOW_HEIGHT - 30,
            text="Avoid obstacles and climb higher!",
            font=("Arial", 10), fill=COLOR_GRAY)

    # ─── Game Screen ───

    def _start_game(self):
        self._clear_ui()
        self.state = self.STATE_PLAYING
        self.score = 0
        self.height = 0
        self.difficulty = 1
        self.spawn_timer = 0
        self.frame_count = 0
        self.game_over_reason = ""
        self.obstacles = []

        self.dragon = Dragon(self.canvas, self._images["dragon"])

        self._build_hud()
        self._build_game_buttons()

    def _build_hud(self):
        self._ui_elements["score_label"] = self.canvas.create_text(
            10, 10, text="Score: 0", font=("Arial", 14, "bold"),
            fill=COLOR_WHITE, anchor=tk.NW)

        self._ui_elements["height_label"] = self.canvas.create_text(
            WINDOW_WIDTH - 10, 10, text="Height: 0m",
            font=("Arial", 14, "bold"), fill=COLOR_WHITE, anchor=tk.NE)

        self._ui_elements["best_label"] = self.canvas.create_text(
            WINDOW_WIDTH // 2, 10, text=f"Best: {self.best_score}",
            font=("Arial", 12), fill=COLOR_YELLOW, anchor=tk.N)

        self._ui_elements["diff_label"] = self.canvas.create_text(
            10, 35, text=f"Difficulty: {self.difficulty}",
            font=("Arial", 11), fill=COLOR_GRAY, anchor=tk.NW)

    def _build_game_buttons(self):
        btn_w, btn_h = 130, 50
        gap = 15
        total_w = btn_w * 2 + gap
        start_x = (WINDOW_WIDTH - total_w) // 2
        btn_y = WINDOW_HEIGHT - 70

        self._add_button("top", start_x, btn_y, btn_w, btn_h,
                         "TOP", COLOR_BUTTON_TOP, self._on_top_press)
        self._add_button("bottom", start_x + btn_w + gap, btn_y, btn_w, btn_h,
                         "BOTTOM", COLOR_BUTTON_BOTTOM, self._on_bottom_press)

    def _on_top_press(self):
        if self.state == self.STATE_PLAYING and self.dragon:
            self.dragon.move_up()
            self.sound.play_async("jump")

    def _on_bottom_press(self):
        if self.state == self.STATE_PLAYING and self.dragon:
            self.dragon.move_down()
            self.sound.play_async("jump")

    # ─── Pause ───

    def _toggle_pause(self):
        if self.state == self.STATE_PLAYING:
            self.state = self.STATE_PAUSED
            self._show_pause_overlay()
        elif self.state == self.STATE_PAUSED:
            self.state = self.STATE_PLAYING
            self._hide_pause_overlay()

    def _show_pause_overlay(self):
        self._ui_elements["pause_bg"] = self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill=COLOR_BLACK, stipple="gray50")
        self._ui_elements["pause_text"] = self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30,
            text="PAUSED", font=("Arial", 36, "bold"), fill=COLOR_WHITE)
        self._ui_elements["pause_hint"] = self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20,
            text="Press P to resume", font=("Arial", 14), fill=COLOR_GRAY)

        self._add_button("resume", WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 + 50,
                         160, 45, "RESUME", COLOR_GREEN, self._toggle_pause)
        self._add_button("quit_menu", WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 + 110,
                         160, 45, "MAIN MENU", COLOR_BLUE, self._return_to_menu)

    def _hide_pause_overlay(self):
        for key in ("pause_bg", "pause_text", "pause_hint"):
            if key in self._ui_elements:
                self.canvas.delete(self._ui_elements[key])
                del self._ui_elements[key]
        if "resume" in self._buttons:
            self._remove_button("resume")
        if "quit_menu" in self._buttons:
            self._remove_button("quit_menu")

    # ─── Game Over ───

    def _game_over(self, reason=""):
        if self.state == self.STATE_GAME_OVER:
            return

        self.state = self.STATE_GAME_OVER
        self.game_over_reason = reason
        self.sound.play_async("crash")

        if self.score > self.best_score:
            self.best_score = self.score
            save_best_score(self.best_score)

        if self.dragon:
            self.dragon.destroy()
            self.dragon = None

        for obs in self.obstacles:
            obs.destroy()
        self.obstacles = []

        self._remove_button("top")
        self._remove_button("bottom")

        self._show_game_over_overlay()

    def _show_game_over_overlay(self):
        cx = WINDOW_WIDTH // 2

        self._ui_elements["go_bg"] = self.canvas.create_rectangle(
            50, 200, WINDOW_WIDTH - 50, 520,
            fill=COLOR_PANEL, outline=COLOR_RED, width=3)

        self._ui_elements["go_title"] = self.canvas.create_text(
            cx, 240, text="GAME OVER", font=("Arial", 30, "bold"),
            fill=COLOR_RED)

        if self.game_over_reason:
            self._ui_elements["go_reason"] = self.canvas.create_text(
                cx, 280, text=self.game_over_reason, font=("Arial", 12),
                fill=COLOR_GRAY)

        self._ui_elements["go_score"] = self.canvas.create_text(
            cx, 320, text=f"Score: {self.score}", font=("Arial", 18, "bold"),
            fill=COLOR_WHITE)

        self._ui_elements["go_height"] = self.canvas.create_text(
            cx, 350, text=f"Height: {int(self.height)}m", font=("Arial", 14),
            fill=COLOR_WHITE)

        if self.score >= self.best_score and self.score > 0:
            self._ui_elements["go_new_best"] = self.canvas.create_text(
                cx, 385, text="NEW BEST SCORE!", font=("Arial", 14, "bold"),
                fill=COLOR_YELLOW)
        else:
            self._ui_elements["go_best"] = self.canvas.create_text(
                cx, 385, text=f"Best: {self.best_score}", font=("Arial", 14),
                fill=COLOR_ORANGE)

        self._add_button("restart", cx - 90, 420, 180, 45,
                         "RESTART", COLOR_GREEN, self._start_game)
        self._add_button("menu", cx - 90, 475, 180, 40,
                         "MAIN MENU", COLOR_BLUE, self._return_to_menu)

    def _return_to_menu(self):
        if self.dragon:
            self.dragon.destroy()
            self.dragon = None
        for obs in self.obstacles:
            obs.destroy()
        self.obstacles = []
        self.state = self.STATE_MENU
        self._build_menu()

    # ─── Game Loop ───

    def _loop(self):
        if not self._running:
            return

        now = time.time()
        dt = now - self._last_time
        self._last_time = now

        if self.state == self.STATE_PLAYING:
            self._update_game()

        self.root.after(int(1000 / FPS), self._loop)

    def _update_game(self):
        self.frame_count += 1

        if self._key_up:
            self.dragon.move_up()
        if self._key_down:
            self.dragon.move_down()

        self.dragon.update()

        self._spawn_obstacles()
        self._update_obstacles()

        self.score += SCORE_PER_FRAME
        self.height += HEIGHT_PER_FRAME

        new_diff = 1 + self.score // DIFFICULTY_INTERVAL
        if new_diff != self.difficulty:
            self.difficulty = new_diff
            self.sound.play_async("score")

        self._check_collisions()
        self._update_hud()

    def _spawn_obstacles(self):
        self.spawn_timer += 1
        interval = max(40, OBSTACLE_SPAWN_INTERVAL - self.difficulty * 5)

        if self.spawn_timer >= interval:
            self.spawn_timer = 0
            speed = OBSTACLE_BASE_SPEED + self.difficulty * 0.5
            gap = max(OBSTACLE_MIN_GAP, OBSTACLE_MAX_GAP - self.difficulty * 10)

            x = WINDOW_WIDTH + 20

            if random.random() < 0.7:
                gap_start = random.randint(100, WINDOW_HEIGHT - gap - 100)

                top_height = gap_start
                bot_start = gap_start + gap

                if top_height > 30:
                    img_top = self._images.get("obstacle_top")
                    if img_top:
                        obs_top = Obstacle(self.canvas, img_top, x, top_height - 200,
                                           speed, is_top=True)
                        self.obstacles.append(obs_top)

                if bot_start < WINDOW_HEIGHT - 30:
                    img_bot = self._images.get("obstacle_bottom")
                    if img_bot:
                        obs_bot = Obstacle(self.canvas, img_bot, x, bot_start,
                                           speed, is_top=False)
                        self.obstacles.append(obs_bot)
            else:
                if random.random() < 0.5:
                    img_flame = self._images.get("obstacle_flame")
                    if img_flame:
                        fy = random.randint(80, WINDOW_HEIGHT - 80)
                        flame = FlameObstacle(self.canvas, img_flame, x, fy,
                                              FLAME_BASE_SPEED + self.difficulty * 0.3)
                        self.obstacles.append(flame)

    def _update_obstacles(self):
        alive = []
        for obs in self.obstacles:
            obs.update()
            if obs.is_offscreen():
                obs.destroy()
            else:
                alive.append(obs)
        self.obstacles = alive

    def _check_collisions(self):
        if not self.dragon or not self.dragon.alive:
            return

        dragon_bbox = self.dragon.get_bbox()

        for obs in self.obstacles:
            obs_bbox = obs.get_bbox()
            if check_collision(dragon_bbox, obs_bbox):
                self._game_over("You hit an obstacle!")
                return

    def _update_hud(self):
        if "score_label" in self._ui_elements:
            self.canvas.itemconfig(self._ui_elements["score_label"],
                                   text=f"Score: {self.score}")
        if "height_label" in self._ui_elements:
            self.canvas.itemconfig(self._ui_elements["height_label"],
                                   text=f"Height: {int(self.height)}m")
        if "best_label" in self._ui_elements:
            self.canvas.itemconfig(self._ui_elements["best_label"],
                                   text=f"Best: {self.best_score}")
        if "diff_label" in self._ui_elements:
            self.canvas.itemconfig(self._ui_elements["diff_label"],
                                   text=f"Difficulty: {self.difficulty}")

    # ─── Keyboard ───

    def _on_key_press(self, event):
        key = event.keysym.lower()

        if key == "p":
            if self.state in (self.STATE_PLAYING, self.STATE_PAUSED):
                self._toggle_pause()
            return

        if key == "m":
            enabled = self.sound.toggle()
            return

        if key == "r" and self.state == self.STATE_GAME_OVER:
            self._start_game()
            return

        if key == "escape":
            if self.state == self.STATE_PLAYING:
                self._toggle_pause()
            elif self.state == self.STATE_PAUSED:
                self._return_to_menu()
            return

        if self.state == self.STATE_PLAYING:
            if key in ("up", "w"):
                self._key_up = True
                self.dragon.move_up()
            elif key in ("down", "s"):
                self._key_down = True
                self.dragon.move_down()
            elif key == "space":
                self.dragon.boost()
                self.sound.play_async("jump")

        if self.state == self.STATE_MENU:
            if key in ("return", "space"):
                self._start_game()

    def _on_key_release(self, event):
        key = event.keysym.lower()
        if key in ("up", "w"):
            self._key_up = False
        elif key in ("down", "s"):
            self._key_down = False

    # ─── UI Helpers ───

    def _add_button(self, name, x, y, w, h, text, color, command):
        btn_id = self.canvas.create_rectangle(x, y, x + w, y + h,
                                              fill=color, outline=COLOR_WHITE, width=2)
        text_id = self.canvas.create_text(x + w // 2, y + h // 2, text=text,
                                          font=("Arial", 14, "bold"), fill=COLOR_WHITE)

        def on_click(e):
            command()

        def on_enter(e):
            self.canvas.itemconfig(btn_id, fill=COLOR_BUTTON_HOVER)

        def on_leave(e):
            self.canvas.itemconfig(btn_id, fill=color)

        self.canvas.tag_bind(btn_id, "<Button-1>", on_click)
        self.canvas.tag_bind(btn_id, "<Enter>", on_enter)
        self.canvas.tag_bind(btn_id, "<Leave>", on_leave)
        self.canvas.tag_bind(text_id, "<Button-1>", on_click)

        self._buttons[name] = (btn_id, text_id)

    def _remove_button(self, name):
        if name in self._buttons:
            btn_id, text_id = self._buttons[name]
            self.canvas.delete(btn_id)
            self.canvas.delete(text_id)
            del self._buttons[name]

    def _clear_ui(self):
        for key, elem_id in list(self._ui_elements.items()):
            self.canvas.delete(elem_id)
        self._ui_elements = {}

        for name in list(self._buttons.keys()):
            self._remove_button(name)

    def stop(self):
        self._running = False