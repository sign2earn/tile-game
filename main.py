# main.py — Kivy rewrite of your Pygame Tile Match Explorer
# Tested with: Kivy >= 2.3.0
# Project layout expected:
#   main.py
#   game.kv
#   assets/
#     background.jpg
#     tiles/*.png|jpg
#     sounds/click.wav, match.wav, lose.wav, bg_music.mp3 (or .ogg)

from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle, Ellipse, Line, InstructionGroup
from kivy.properties import (
    NumericProperty, ListProperty, StringProperty, BooleanProperty, ObjectProperty
)
import random, os, time

WIDTH, HEIGHT = 900, 700
TILE_FOLDER = os.path.join('assets', 'tiles')
BG_IMAGE_PATH = os.path.join('assets', 'background.jpg')
BG_MUSIC_PATH = os.path.join('assets', 'sounds', 'bg_music.mp3')
CLICK_SOUND_PATH = os.path.join('assets', 'sounds', 'click.wav')
MATCH_SOUND_PATH = os.path.join('assets', 'sounds', 'match.wav')
LOSE_SOUND_PATH = os.path.join('assets', 'sounds', 'lose.wav')

TILE_SIZE = 60
MAX_HOLD = 7
SCORE_PER_MATCH = 10
TIMER_LIMIT = 180
MAX_GRID_SIZE = 12
MAX_LAYERS = 3

class Tile(Widget):
    source = StringProperty('')
    tile_id = NumericProperty(0)
    layer = NumericProperty(0)
    gx = NumericProperty(0)  # grid x
    gy = NumericProperty(0)  # grid y

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._col = Color(1,1,1,1)
            self._rect_bg = Rectangle(pos=self.pos, size=self.size)
            self._rect = Rectangle(source=self.source, pos=self.pos, size=self.size)
            self._border = Line(rectangle=(*self.pos, *self.size), width=1.2)
        self.bind(pos=self._sync, size=self._sync, source=self._sync_source)

    def _sync(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect_bg.pos = self.pos
        self._rect_bg.size = self.size
        self._border.rectangle = (*self.pos, *self.size)

    def _sync_source(self, *args):
        self._rect.source = self.source

class FloatingSprite(Widget):
    """For match animation: fade out and move down."""
    source = StringProperty('')
    alpha = NumericProperty(1.0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._col = Color(1,1,1,self.alpha)
            self._rect = Rectangle(source=self.source, pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync, alpha=self._sync_alpha, source=self._sync_source)

    def _sync(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _sync_alpha(self, *args):
        self._col.a = self.alpha

    def _sync_source(self, *args):
        self._rect.source = self.source

class Particle(Widget):
    """Simple particle as a small circle moving upward then dying."""
    life = NumericProperty(20)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._col = Color(1,1,1,1)
            self._circ = Ellipse(pos=self.pos, size=(8,8))
        self.bind(pos=self._sync)

    def _sync(self, *args):
        self._circ.pos = self.pos

class GameBoard(FloatLayout):
    score = NumericProperty(0)
    level = NumericProperty(1)
    remaining = NumericProperty(TIMER_LIMIT)
    game_won = BooleanProperty(False)
    game_lost = BooleanProperty(False)
    paused = BooleanProperty(False)

    # UI references injected from KV
    score_label = ObjectProperty(None)
    time_label = ObjectProperty(None)
    level_label = ObjectProperty(None)
    undo_btn = ObjectProperty(None)
    reset_btn = ObjectProperty(None)
    overlay_box = ObjectProperty(None)
    overlay_label = ObjectProperty(None)
    overlay_action_btn = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rng = random.Random()
        self._rng.seed()
        self._raw_images = []  # list of file paths (we'll use source directly)
        self._load_assets()
        self._bg_instr = InstructionGroup()
        with self.canvas.before:
            self._bg_color = Color(1,1,1,1)
            self._bg_rect = Rectangle(source=BG_IMAGE_PATH if os.path.exists(BG_IMAGE_PATH) else '', pos=(0,0), size=(WIDTH, HEIGHT))

        self.grid_tiles = []  # Tile widgets in the board
        self.held_tiles = []  # list[Tile]
        self.undo_stack = []  # stack of {"tile": tile_widget, "parent_index": index}
        self._start_time = time.time()
        self.particles = []
        self._matched_sprites = []

        # Buttons / labels will be created by KV; music/sounds here
        self._init_audio()

        # Start level
        self._shake_timer = 0
        self.next_level(reset=True)

        self._ticker = Clock.schedule_interval(self.update, 1/60.0)

    # ------------ Asset & Audio -------------
    def _load_assets(self):
        if os.path.isdir(TILE_FOLDER):
            for fn in os.listdir(TILE_FOLDER):
                if fn.lower().endswith(('.png','.jpg','.jpeg','.webp')):
                    self._raw_images.append(os.path.join(TILE_FOLDER, fn))
        self._raw_images.sort()

    def _init_audio(self):
        self.click_sound = SoundLoader.load(CLICK_SOUND_PATH) if os.path.exists(CLICK_SOUND_PATH) else None
        self.match_sound = SoundLoader.load(MATCH_SOUND_PATH) if os.path.exists(MATCH_SOUND_PATH) else None
        self.lose_sound = SoundLoader.load(LOSE_SOUND_PATH) if os.path.exists(LOSE_SOUND_PATH) else None
        # Background music
        self._bg_music = SoundLoader.load(BG_MUSIC_PATH) if os.path.exists(BG_MUSIC_PATH) else None
        if self._bg_music:
            try:
                self._bg_music.loop = True
            except Exception:
                pass
            self._bg_music.play()

    # ------------- Level / Grid ---------------
    def get_grid_size(self, level):
        base = 6
        size = base + (level - 1) // 3
        size = min(size, MAX_GRID_SIZE)
        return size, size

    def generate_tiles(self, level):
        rows, cols = self.get_grid_size(level)
        base_total = 18
        total_tiles = base_total + (level - 1) * 3
        if total_tiles % 3 != 0:
            total_tiles += (3 - total_tiles % 3)

        num_groups = total_tiles // 3
        max_images = min(len(self._raw_images), 6 + (level - 1) // 3)
        num_unique_images = min(num_groups, max_images)
        if num_unique_images == 0:
            # Fallback to a dummy tile if assets missing
            self._raw_images = [os.path.join('assets','tiles','__missing.png')]
            num_unique_images = 1

        selected_images = self._rng.sample(self._raw_images[:max_images] or self._raw_images, num_unique_images)

        tiles = []
        img_index = 0
        for _ in range(num_groups):
            src = selected_images[img_index % num_unique_images]
            for _ in range(3):
                tiles.append({"src": src, "id": img_index % num_unique_images})
            img_index += 1
        self._rng.shuffle(tiles)
        return tiles, rows, cols

    def create_grid(self, tiles, rows, cols):
        # Clear previous tiles
        for t in list(self.grid_tiles):
            self.remove_widget(t)
        self.grid_tiles.clear()

        layer_offset = 15
        idx = 0
        grid_width = cols * (TILE_SIZE - 15) + 15
        grid_height = rows * (TILE_SIZE - 25) + 25
        start_x = (WIDTH - grid_width) // 2
        start_y = (HEIGHT - grid_height) // 2 + 70

        for layer in range(MAX_LAYERS):
            for row in range(rows):
                for col in range(cols):
                    if idx >= len(tiles): break
                    x = start_x + col * (TILE_SIZE - 15)
                    y = start_y + row * (TILE_SIZE - 25) - layer * layer_offset
                    tile = Tile(pos=(x,y), size=(TILE_SIZE, TILE_SIZE),
                                source=tiles[idx]["src"], tile_id=tiles[idx]["id"],
                                layer=layer, gx=col, gy=row)
                    self.add_widget(tile)
                    self.grid_tiles.append(tile)
                    idx += 1

    def is_tile_free(self, tile):
        # A tile is free if no tile with same gx/gy has a higher layer
        for t in self.grid_tiles:
            if t.gx == tile.gx and t.gy == tile.gy and t.layer > tile.layer:
                return False
        return True

    # ------------- UI & Flow -----------------
    def format_time(self, seconds):
        seconds = max(0, int(seconds))
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"

    def next_level(self, reset=False):
        if not reset:
            self.level += 1
        tiles, self.ROWS, self.COLS = self.generate_tiles(self.level)
        self.create_grid(tiles, self.ROWS, self.COLS)
        self.held_tiles.clear()
        self.undo_stack.clear()
        self.game_won = False
        self.game_lost = False
        self.paused = False
        self._start_time = time.time()
        if reset:
            self.score = 0
        # update labels if ready
        if self.level_label:
            self.level_label.text = f"Level: {self.level}"

    def on_touch_down(self, touch):
        if self.game_won or self.game_lost:
            return super().on_touch_down(touch)

        # Buttons area is handled by Kivy; we only consume touches on tiles / held slots
        # Find top-most tile under touch that is free
        for tile in sorted(self.grid_tiles, key=lambda t:(t.layer, ), reverse=True):
            if tile.collide_point(*touch.pos) and self.is_tile_free(tile):
                # pick tile
                try:
                    idx = self.grid_tiles.index(tile)
                except ValueError:
                    idx = -1
                self.undo_stack.append({"tile": tile, "pos": idx})
                self.grid_tiles.remove(tile)
                self.remove_widget(tile)  # remove from board
                # Create a small clone to display in hold slots (re-using the same widget is fine: we keep it detached)
                self.held_tiles.append(tile)
                if self.click_sound: self.click_sound.play()
                break

        if len(self.held_tiles) > MAX_HOLD and not self.game_lost:
            self.game_lost = True
            if self.lose_sound: self.lose_sound.play()
            self._shake_timer = 20
        return super().on_touch_down(touch)

    # Button actions (bound in .kv)
    def do_undo(self, *args):
        if self.held_tiles and self.undo_stack:
            last = self.undo_stack.pop()
            tile = self.held_tiles.pop()
            # reinsert tile to grid
            if last["pos"] < 0 or last["pos"] > len(self.grid_tiles):
                self.grid_tiles.append(tile)
            else:
                self.grid_tiles.insert(last["pos"], tile)
            self.add_widget(tile)  # back to board
            if self.click_sound: self.click_sound.play()

    def do_reset(self, *args):
        if self.click_sound: self.click_sound.play()
        self.level = max(1, self.level)
        self.next_level(reset=True)

    def do_overlay_action(self, *args):
        if self.game_won:
            # particle burst
            for _ in range(30):
                p = Particle(pos=(WIDTH//2, HEIGHT//2))
                self.add_widget(p)
                self.particles.append(p)
            if self.click_sound: self.click_sound.play()
            self.next_level(reset=False)
        elif self.game_lost:
            if self.click_sound: self.click_sound.play()
            self.next_level(reset=True)

    # ------------- Matching & Animations ---------------
    def check_matches(self):
        counter = {}
        for t in self.held_tiles:
            counter[t.tile_id] = counter.get(t.tile_id, 0) + 1
        for tid, cnt in counter.items():
            if cnt >= 3:
                removed = 0
                new_list = []
                for idx, t in enumerate(self.held_tiles):
                    if t.tile_id == tid and removed < 3:
                        # spawn floating sprite at hold slot position
                        slot_x = 150 + idx * (TILE_SIZE + 10)
                        slot_y = 80
                        fs = FloatingSprite(pos=(slot_x, slot_y), size=(TILE_SIZE, TILE_SIZE), source=t.source, alpha=1.0)
                        self.add_widget(fs)
                        self._matched_sprites.append({"spr": fs, "step": 0})
                        removed += 1
                    else:
                        new_list.append(t)
                self.held_tiles = new_list
                self.score += SCORE_PER_MATCH
                if self.match_sound: self.match_sound.play()
                break

    def update_matched_sprites(self):
        for entry in list(self._matched_sprites):
            spr = entry["spr"]
            step = entry["step"]
            spr.pos = (spr.x, spr.y + 4)
            spr.alpha = max(0.0, 1.0 - step * 0.08)
            entry["step"] += 1
            if entry["step"] >= 15:
                self.remove_widget(spr)
                self._matched_sprites.remove(entry)

    def update_particles(self):
        for p in list(self.particles):
            p.pos = (p.x + random.randint(-5,5), p.y + 5)
            p.life -= 1
            if p.life <= 0:
                self.remove_widget(p)
                self.particles.remove(p)

    # ------------- Game Loop ---------------
    def update(self, dt):
        # Background
        if os.path.exists(BG_IMAGE_PATH):
            self._bg_rect.source = BG_IMAGE_PATH
        self._bg_rect.size = (WIDTH, HEIGHT)

        elapsed = int(time.time() - self._start_time)
        remaining = max(0, TIMER_LIMIT - elapsed)
        self.remaining = remaining

        # Labels
        if self.score_label:
            self.score_label.text = f"Score: {self.score}"
        if self.time_label:
            self.time_label.text = f"Time: {self.format_time(self.remaining)}"
        if self.level_label:
            self.level_label.text = f"Level: {self.level}"

        # Overlay visibility
        self.overlay_box.opacity = 1 if (self.game_won or self.game_lost) else 0
        if self.game_won:
            self.overlay_label.text = "🎉 Victory!"
            self.overlay_action_btn.text = "Next Level"
        elif self.game_lost:
            self.overlay_label.text = "💥 You Lost!"
            self.overlay_action_btn.text = "Try Again"

        # Timeout
        if not self.paused and not self.game_lost and not self.game_won and remaining <= 0:
            self.game_lost = True
            if self.lose_sound: self.lose_sound.play()
            self._shake_timer = 20

        # Match check
        if not (self.game_won or self.game_lost):
            self.check_matches()

        # Win state
        if not self.grid_tiles and not self.held_tiles and not self.game_won:
            self.game_won = True

        # Animations
        self.update_matched_sprites()
        self.update_particles()

        # (Optional) shake effect could be simulated by nudging root pos, skipped here for simplicity.

class TileExplorerApp(App):
    def build(self):
        Window.size = (WIDTH, HEIGHT)
        return GameBoard()

if __name__ == "__main__":
    TileExplorerApp().run()
