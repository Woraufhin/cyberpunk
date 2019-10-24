import logging
from pathlib import Path
from dataclasses import dataclass, field

import pygame as pg

import chess.settings as s
from chess.panels.panel import Panel
from chess.utils.coords import Coords
from chess.utils.typewriter import Typewriter, TypewriterConfig


logger = logging.getLogger(Path(__file__).stem)


@dataclass(eq=False)
class Backdrop(Panel):
    color: tuple = s.BLACK
    alpha: int = 100

    def __post_init__(self):
        super().__post_init__()


@dataclass(eq=False)
class Promotion(Panel):

    title = 'Promotion'
    color: tuple = s.BLACK
    margin: int = 12
    frame_offset: int = s.TILESIZE * 2

    def __post_init__(self):
        super().__post_init__()
        self.frame, self.rect = self.draw_frame()

    def draw_frame(self):
        rect = pg.Rect(
            self.margin,
            self.frame_offset,
            self.image.get_width() - self.margin * 2,
            self.image.get_height() - self.margin - self.frame_offset
        )
        frame = self.image.subsurface(rect)
        frame.fill(s.BLACK)
        return frame, rect

    def draw_pixel_art(self):
        if self.draw_px_art:
            px = s.TILESIZE / 4
            pg.draw.rect(self.image, self.parent_color, (0, 0, px, px))
            pg.draw.rect(self.image, self.parent_color, (0, self.image.get_height() - px, px, px))
            pg.draw.rect(
                self.image, self.parent_color,
                (self.image.get_width() - px, self.image.get_height() - px, px, px)
            )
            pg.draw.rect(self.image, self.parent_color, (self.image.get_width() - px, 0, px, px))
