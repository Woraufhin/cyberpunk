import math
import logging
from collections import namedtuple
from pathlib import Path
from dataclasses import dataclass
from typing import List, ClassVar, Tuple, Dict
from enum import Enum

import pygame as pg

import chess.settings as s
from chess.utils.coords import Coords


logger = logging.getLogger(Path(__file__).stem)


class LogType(Enum):
    ERROR = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3
    CUSTOM = 4


@dataclass
class TypewriterConfig:
    size: int = 16
    color: tuple = s.GREEN
    surface_color: tuple = s.BLACK
    pos: str = 'topleft'
    padding: int = 10
    bold: int = 2
    positions: ClassVar[List[str]] = [
        'topleft', 'midtop', 'topright',
        'midleft', 'center', 'midright',
        'bottomleft', 'midbottom', 'bottomright'
    ]

    def __post_init__(self):
        if self.pos not in self.positions:
            raise ValueError(f'"{self.pos}" is not a valid pos value. '
                             f'Should be {self.positions!r}')


@dataclass
class Typewriter:
    surface: 'pg.Surface'
    config: 'TypewriterConfig' = TypewriterConfig()

    def type(self, text: str, coords: Coords = None, config: TypewriterConfig = None):
        conf = config if config else self.config
        font = self.get_font(conf.size, conf.bold)

        text_surf = font.render(
            # this function takes no keyword args...
            text,       # text
            False,       # antialias
            conf.color  # color
        )
        text_rect = self.position(text_surf.get_rect(), conf.pos, coords)
        self.surface.blit(text_surf, text_rect)

    def log(self, text: List[Tuple['LogType', str]],
            top_down: bool = False,
            configs: Dict['LogType', 'TypewriterConfig'] = None):
        """ Intelligently print within surface.
        This behaves as if surface were a normal console """

        max_w, max_h = self.surface.get_width(), self.surface.get_height() - self.line_size
        x, y = self.config.padding, max_h
        if top_down:
            x, y = self.config.padding, self.config.padding
        font = self.get_font(self.config.size, self.config.bold)

        # fill screen to re-draw
        self.surface.fill(self.config.surface_color)

        # honor new lines
        text = self._process_newlines(text)

        if not top_down:
            text = reversed(text)
        for type, entry in text:
            if y < 0 or y > max_h:
                # this was a huge optimization :P
                break
            try:
                conf = configs[type]
            except IndexError:
                conf = self.config
            if not top_down:
                # calculate how many rows we need to print entry when
                # we're typing bottom-up
                line = self._calculate_lines_needed(
                    entry, conf, font, max_w
                )
                y -= line.need * line.height
            for word in entry.split(' '):
                word_surface = font.render(word, True, conf.color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_w:
                    x = conf.padding  # Reset the x.
                    y += word_height  # Start on new row.
                self.surface.blit(word_surface, (x, y))
                x += word_width + self.space_size[0]
            x = conf.padding  # Reset the x.
            if not top_down:
                y -= word_height * (line.need - 1)  # Calculate new offset position
            else:
                y += word_height

    def _calculate_lines_needed(self, line, conf, font, max_width):
        Line = namedtuple('Line', ['need', 'width', 'height'])
        line_surface = font.render(line, True, conf.color)
        line_width, line_height = line_surface.get_size()
        lines_needed = int(math.ceil(
            line_width / (max_width - conf.padding * 2)
        ))
        return Line(lines_needed, line_width, line_height)

    def _process_newlines(self, text):
        new_text = []
        for type, line in text:
            if "\n" in line:
                new_text.extend(map(lambda x: (type, x), line.split("\n")))
            else:
                new_text.append((type, line))
        return new_text

    def position(self, text_rect, pos, coords):
        s_rect = self.surface.get_rect()
        if coords:
            text_rect.topleft = coords
        elif pos == 'center':
            text_rect.center = s_rect.center
        elif pos == 'topleft':
            padding = Coords(x=self.config.padding, y=self.config.padding)
            text_rect.topleft = s_rect.topleft + padding
        elif pos == 'midtop':
            padding = Coords(x=0, y=self.config.padding)
            text_rect.midtop = s_rect.midtop + padding
        elif pos == 'topright':
            padding = Coords(x=-self.config.padding, y=self.config.padding)
            text_rect.topright = s_rect.topright + padding
        elif pos == 'midleft':
            padding = Coords(x=self.config.padding, y=0)
            text_rect.midleft = s_rect.midleft + padding
        elif pos == 'midright':
            padding = Coords(x=-self.config.padding, y=0)
            text_rect.midright = s_rect.midright + padding
        elif pos == 'bottomleft':
            padding = Coords(x=self.config.padding, y=-self.config.padding)
            text_rect.bottomleft = s_rect.bottomleft + padding
        elif pos == 'midbottom':
            padding = Coords(x=0, y=-self.config.padding)
            text_rect.midbottom = s_rect.midbottom + padding
        elif pos == 'bottomright':
            padding = Coords(x=-self.config.padding, y=-self.config.padding)
            text_rect.bottomright = s_rect.bottomright + padding
        return text_rect

    def get_text_size(self, text):
        return self.get_font(
            size=self.config.size,
            bold=self.config.bold
        ).size(text)

    @staticmethod
    def get_font(size, bold):
        font = pg.font.Font(s.FONT_PATH, size)
        font.set_bold(bold)
        return font

    @property
    def space_size(self):
        return self.get_text_size(' ')

    @property
    def line_size(self):
        return self.get_font(
            size=self.config.size,
            bold=self.config.bold
        ).get_linesize()
