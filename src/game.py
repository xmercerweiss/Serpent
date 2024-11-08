from collections import deque
from random import randrange
from time import sleep
from sys import exit

import keyboard as keyb

from utils import _Configurable, raise_error
from .graphics import _Renderer


class Snake(_Configurable):

    _CONFIG_ATTRS = {
        # Attribute:    (key in conf,   default )
        "_DELAY":       ("delay",           0.5), # Seconds
        "_APP_LENGTH":  ("length",          15  ), # Tiles
        "_APP_HEIGHT":  ("height",          15  ), # Tiles
        "_FRUIT_COUNT": ("fruit_count",     1   ),
        "_INIT_LEN":    ("init_snake_size", 4   ), # Initial snake length
        "_GRASS":       ("grass_texture",   "g" ), # Texture, from src.graphics._Renderer.textures
        "_SNAKE":       ("snake_texture",   "b" ),
        "_FRUIT":       ("fruit_texture",   "r" ),
    }

    _HEADINGS = {
        "w":        ( 0, -1),
        "k":        ( 0, -1),
        "up":       ( 0, -1),
        "a":        (-1,  0),
        "h":        (-1,  0),
        "left":     (-1,  0),
        "s":        ( 0,  1),
        "j":        ( 0,  1),
        "down":     ( 0,  1),
        "d":        ( 1,  0),
        "l":        ( 1,  0),
        "right":    ( 1,  0),
    }

    _ESC_KEY = "esc"
    _PAUSE_KEY = "space"

    _HEADING_KEYS = set(k for k in _HEADINGS.keys())
    
    _VALID_KEYS = _HEADING_KEYS | {
        _ESC_KEY,
        _PAUSE_KEY
    }

    _DELAY_DIV = 10
    # Given a delay in seconds t (self._DELAY), t seconds will pass between each display update.
    # Given an integer d (self._DELAY_DIV), the current input will be assessed every t/d seconds,
    # resulting in d instances of the current input being assessed between each render.

    # This is done to allow more responsive game movement, at the cost of performance.

    _INV_RENDERER_ERR = \
    "{} attempted to instantiate class {} as a renderer; renderers must be derived from _Renderer."

    def __init__(self, renderer_cls, renderer_conf=(), **conf):
        self.__init_keyboard()
        self._RENDERER = self.__init_renderer(renderer_cls, renderer_conf)
        self._snake = deque()
        self._score = None
        self._current_heading = (1, 0)
        self._last_heading = None
        self._fruits = set()
        self._pressed_keys = set()
        self._paused = False

    def __init_keyboard(self):
        for key in self._VALID_KEYS:
            keyb.on_press_key(key, callback=self.__register_key_press)
            keyb.on_release_key(key, callback=self.__register_key_release)
    
    @staticmethod
    def __init_renderer(cls, conf):
        if issubclass(cls, _Renderer):
            return cls(**conf)
        raise_error(
            cls.__name__,
            cls.__name__,
            e=TypeError,
            msg=cls._INV_RENDERER_ERR
        )
    
    def __register_key_press(self, event):
        self._pressed_keys.add(event.name)

    def __register_key_release(self, event):
        self._pressed_keys.remove(event.name)
    
    def start(self):
        self._spawn_snake()
        for _ in range(self._FRUIT_COUNT):
            self._spawn_fruit()
        self._mainloop()

    def stop(self):
        self._snake.clear()
        self._score = None
        self._fruits = set()
        self._paused = False

    def _spawn_snake(self):
        y = self._APP_HEIGHT // 2
        self._snake = deque(
            (x, y) for x in range(1, self._INIT_LEN + 1)
        )
        self._snake.reverse()
        self._score = 0

    def _spawn_fruit(self):
        if len(self._fruits) >= self._FRUIT_COUNT:
            return
        x, y = randrange(self._APP_LENGTH), randrange(self._APP_HEIGHT)
        while self._is_snake_tile(x, y) or self._is_fruit_tile(x, y):
            x, y = randrange(self._APP_LENGTH), randrange(self._APP_HEIGHT)
        self._fruits.add(
            (x, y)
        )

    def _mainloop(self):
        while self._snake:
            self._accept_input()
            if not self._paused:
                self._move_snake()
                self._update_display()

    def _accept_input(self):
        for _ in range(self._DELAY_DIV):
            if self._ESC_KEY in self._pressed_keys:
                exit(0)
            elif self._PAUSE_KEY in self._pressed_keys:
                self._paused = not self._paused
            headers = self._HEADING_KEYS & self._pressed_keys
            if len(headers) == 1:
                new = self._HEADINGS[headers.pop()]
                if self._last_heading != tuple(x * -1 for x in new):
                    self._current_heading = new
            sleep(self._DELAY / self._DELAY_DIV)

    def _move_snake(self):
        head = self._snake[0]
        candidate = (
            head[0] + self._current_heading[0],
            head[1] + self._current_heading[1],
        )
        if not self._is_valid_tile(*candidate) or self._is_snake_tile(*candidate):
            self.stop()
            return
        if self._is_fruit_tile(*candidate):
            self._fruits.remove(candidate)
            self._score += 1
            self._spawn_fruit()
        else:
            self._snake.pop()
        self._snake.appendleft(candidate)
        self._last_heading = self._current_heading

    def _update_display(self):
        self._RENDERER.set_scene(
                self._APP_LENGTH,
                self._APP_HEIGHT,
                self._GRASS
            )
        self._RENDERER.add_tiles(
            tuple(self._snake),
            self._SNAKE
        )
        self._RENDERER.add_tiles(
            self._fruits,
            self._FRUIT
        )
        self._RENDERER.render_scene()

    def _is_valid_tile(self, x, y):
        return 0 <= x < self._APP_LENGTH and 0 <= y < self._APP_HEIGHT

    def _is_snake_tile(self, x, y):
        return (x, y) in self._snake

    def _is_fruit_tile(self, x, y):
        return (x, y) in self._fruits
