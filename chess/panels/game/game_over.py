import logging
from pathlib import Path
from dataclasses import dataclass

import pygame as pg

import chess.settings as s
from chess.panels.panel import Panel
from chess.panels.backdrop import Backdrop
from chess.panels.intro.button import Button

from chess.utils.coords import Coords


logger = logging.getLogger(Path(__file__).stem)


@dataclass(eq=False)
class GameOver(Panel):

    title: str = 'Checkmate!'
    color: tuple = s.BLACK
    draw_px_art: bool = False
    margin: int = 12
    frame_offset: int = s.TILESIZE * 2

    def __post_init__(self):
        self.backdrop = Backdrop(
            sprite_group=self.sprite_group,
            pos=Coords(x=0, y=0),
            size=Coords(x=s.GRIDWIDTH, y=s.GRIDHEIGHT)
        )
        super().__post_init__()
        self.frame, self.f_rect = self.draw_frame()
        #self.buttons = self.draw_buttons()

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