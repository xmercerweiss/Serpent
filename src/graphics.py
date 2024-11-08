from abc import abstractmethod
from numbers import Integral
from os import system as bash
import itertools as it

import pygame as pyg

from utils import _Configurable, raise_error


class _Renderer(_Configurable):

    _NULL_TEXTURE = "NULL"

    _TEXTURES = (
        "r",    # Red
        "g",    # Green
        "b",    # Blue
        "c",    # Cyan
        "m",    # Magenta
        "y",    # Yellow
        "w",    # White
        "k",    # Black
        _NULL_TEXTURE
    )

    _TILE_STR = "({}, {})"
    _CHAR_STR = "{} "

    _INV_DIST_ERR = \
    "Invalid distance {} passed to {}. Distances must be positive integer values."

    _INV_TILE_ERR = \
    "Invalid tile {} passed to {}. Coordinates must contain natural numbers which fall within the bounds of the current scene."

    _INV_CONF_ERR = \
    "Config value {} missing or invalid within {}, please review configuration."

    def __init__(self, **conf):
        self._textures = {}
        self._scene = {}
        self._text = []
        self._field_length = 0
        self._field_height = 0
        self._field_texture = None
        self.__init_values(conf)

    def __init_values(self, conf):
        if self._NULL_TEXTURE not in conf.keys():
            self._raise_config_error(self._NULL_TEXTURE)
        self._textures = {k:v for k, v in conf.items() if k in self._TEXTURES}
        self._textures[None] = conf[self._NULL_TEXTURE]

    @staticmethod
    def is_valid_distance(n):
        return n >= 0 and isinstance(n, Integral)

    @property
    def null_texture(self):
        return self._NULL_TEXTURE

    @property
    def textures(self):
        return self._TEXTURES

    @abstractmethod
    def _render_tile(self, x, y, texture):
        pass

    def set_scene(self, l, h, texture=None):
        self._validate_bounds(l, h)
        self._pre_setting()
        self._scene = {}
        self._text = []
        self._field_length = l
        self._field_height = h
        self._field_texture = texture
        self._post_setting()

    def render_scene(self):
        self._pre_render()

        for y in range(self._field_height):
            for x in range(self._field_length):
                texture = self._scene.get((x, y), self._field_texture)
                self._render_tile(x, y, texture)

        self._post_render()

    def add_tiles(self, tiles, texture=None):
        for x, y in tiles:
            self.add_tile(x, y, texture)

    def add_tile(self, x, y, texture=None):
        self._validate_tile(x, y)
        self._scene[(x, y)] = texture

    def add_text(self, x, y, string):
        self._validate_tile(x, y)
        self._text.append(
            ((x, y), string)
        )

    def kill(self):
        del self

    def is_valid_x(self, x):
        return 0 <= x < self._field_length and isinstance(x, Integral)

    def is_valid_y(self, y):
        return 0 <= y < self._field_height and isinstance(y, Integral)

    def _validate_bounds(self, l, h):
        if not self.is_valid_distance(l):
            self._raise_distance_error(l)
        elif not self.is_valid_distance(h):
            self._raise_distance_error(h)

    def _validate_tile(self, x, y):
        if not self.is_valid_x(x) or not self.is_valid_y(y):
            self._raise_tile_error(x, y)

    def _pre_setting(self):
        pass

    def _post_setting(self):
        pass

    def _pre_render(self):
        pass

    def _post_render(self):
        pass

    def _raise_config_error(self, config):
        raise_error(
            config,
            self.__class__.__name__,
            e=ValueError,
            msg=self._INV_CONF_ERR
        )

    def _raise_distance_error(self, distance):
        raise_error(
            distance, 
            self.__class__,__name__, 
            e=ValueError, 
            msg=self._INV_DIST_ERR
        )

    def _raise_tile_error(self, x, y):
        tile = self._TILE_STR.format(x, y)
        raise_error(
            tile, 
            self.__class__.__name__, 
            e=IndexError,
            msg=self._INV_TILE_ERR
        )


class CLIRenderer(_Renderer):

    def __init__(self, **conf):
        super().__init__(**conf)
        self._buffer = []

    def _render_tile(self, x, y, texture):
        char = self._textures[texture]
        self._buffer[y][x] = char

    def _post_setting(self):
        self._buffer = [
            [None for _ in range(self._field_length)] 
            for _ in range(self._field_height)
        ]

    def _pre_render(self):
        bash("clear")

    def _post_render(self):
        self._buffer_text()
        output = "\n".join("".join(l) for l in self._buffer)
        bash(f'echo "{output}"')

    def _buffer_text(self):
        for (x, y), string in self._text:
            l = len(string) + x
            for (i, e) in enumerate(self._buffer[y]):
                if x <= i < l:
                    c = string[i - x]
                    self._buffer[y][i] = self._CHAR_STR.format(c)


class GUIRenderer(_Renderer):

    _CONFIG_ATTRS = {
        # Attribute:    (key in conf,   default     )
        "_TITLE":       ("title",       "renderer"  ),
        "_FONT":        ("font",        "FreeMono"  ),
        "_TILE_SIZE":   ("px_per_tile", 20          ), # Pixels
        "_FONT_SIZE":   ("font_size",   20          )  # Point
    }

    _TEXT_COLOR = (0, 0, 0)

    def __init__(self, **conf):
        super().__init__(**conf)
        self.__init_pygame()
        self._window = None
        self._window_length = None
        self._window_height = None
        self._font_renderer = None
        self.__init_values(conf)

    def __del__(self):
        self.__quit_pygame()

    def __init_pygame(self):
        pyg.init()
        pyg.font.init()
        pyg.display.init()
        pyg.display.set_caption(self._TITLE)

    def __init_values(self, conf):
        self._textures = {k: pyg.Color(v) for k, v in self._textures.items()}
        self._font_renderer = pyg.font.SysFont(self._FONT, self._FONT_SIZE)

    @staticmethod
    def __quit_pygame():
        pyg.display.quit()
        pyg.font.quit()
        pyg.quit()

    def _post_setting(self):
        if self._window_length != self._field_length or self._window_height != self._field_height:
            self._window_length = self._field_length
            self._window_height = self._field_height
            dimensions = (self._field_length * self._TILE_SIZE, self._field_height * self._TILE_SIZE)
            self._window = pyg.display.set_mode(dimensions)

    def _pre_render(self):
        self._window.fill(self._textures[self._field_texture])

    def _post_render(self):
        self._render_text()
        pyg.display.update()

    def _render_tile(self, x, y, texture):
        if texture == self._field_texture:
            return
        tile = (
            x * self._TILE_SIZE,
            y * self._TILE_SIZE,
            self._TILE_SIZE,
            self._TILE_SIZE
        )
        pyg.draw.rect(
            self._window,
            self._textures[texture],
            tile
        )

    def _render_text(self):
        for (x, y), string in self._text:
            text = self._font_renderer.render(string, True, self._TEXT_COLOR)
            destination = (
                x * self._TILE_SIZE,
                y * self._TILE_SIZE
            )
            self._window.blit(text, destination)
