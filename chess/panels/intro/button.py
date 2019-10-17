import logging
from pathlib import Path
from dataclasses import dataclass

import pygame as pg

import chess.settings as s
from chess.utils.coords import Coords
from chess.utils.typewriter import Typewriter, TypewriterConfig


logger = logging.getLogger(Path(__file__).stem)


@dataclass
class Button:
    surface: 'pg.Surface'
    pos: 'Coords'
    size: 'Coords'
    text: str
    config: 'TypewriterConfig' = TypewriterConfig(
        size=32,
        color=s.GREEN,
        pos='center'
    )
    desc: str = ''
    hovering: bool = False

    def __post_init__(self):
        self.scaled_pos = self.pos * s.TILESIZE
        self.scaled_size = self.size * s.TILESIZE
        self.rect = pg.Rect(
            self.scaled_pos.x, self.scaled_pos.y,
            self.scaled_size.x, self.scaled_size.y
        )
        self.surf = self.surface.subsurface(self.rect)
        self.tp = Typewriter(self.surf, self.config)
        self.new()

    def new(self):
        self.surf.fill(s.BLACK)
        self.draw_text()

    def draw_text(self):
        self.tp.type(self.text)

    def update(self):
        if self.hovering:
            self.hover()
        else:
            self.new()

    def hover(self):
        self.surf.fill(s.DARKGREEN)
        self.draw_text()
        pg.draw.rect(
            self.surf, s.GREEN,
            (0, 0, self.scaled_size.x, self.scaled_size.y), 2
        )

    def on_click(self):
        return self.text


@dataclass
class SelectionButton(Button):
    config: 'TypewriterConfig' = TypewriterConfig(
        size=16,
        color=s.GREEN,
        pos='midleft'
    )
    hovering: bool = False
    selected: bool = False

    def new(self):
        if self.selected:
            self.hover()
        else:
            super().new()

    def update(self):
        if self.hovering:
            self.hover()
        else:
            self.new()
        if self.selected:
            self.hover()

    def on_click(self):
        self.selected = not self.selected
        return self.text
