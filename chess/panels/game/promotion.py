import math
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
class Promotion(Panel):

    title: str = 'Promotion'
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
        self.buttons = self.draw_buttons()

    def update(self):
        mpos = self.scale_mouse(pg.mouse.get_pos())
        for button in self.buttons:
            if button.rect.collidepoint(mpos):
                button.hovering = True
            else:
                button.hovering = False
            button.update()

    def scale_mouse(self, mpos):
        mpos = Coords(x=mpos[0], y=mpos[1])
        offset = Coords(x=self.rect.x, y=self.rect.y) + Coords(x=self.margin, y=self.frame_offset)
        return mpos - offset

    def click(self, mpos):
        action = None
        mpos = self.scale_mouse(mpos)
        for button in self.buttons:
            if button.rect.collidepoint(mpos):
                action = button.on_click()
        if action:
            return action

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

    def draw_buttons(self):
        w, h = self.frame.get_width(), self.frame.get_height()
        size = Coords(x=2.4, y=2.4)
        return [
            Button(
                surface=self.frame,
                pos=Coords(x=0, y=0),
                size=size,
                value='queen',
                text='Q'
            ),
            Button(
                surface=self.frame,
                pos=Coords(x=2.4, y=0),
                size=size,
                value='rook',
                text='R'
            ),
            Button(
                surface=self.frame,
                pos=Coords(x=0, y=2.4),
                size=size,
                value='bishop',
                text='B'
            ),
            Button(
                surface=self.frame,
                pos=Coords(x=2.4, y=2.4),
                size=size,
                value='knight',
                text='K'
            )
        ]

    @property
    def promotions(self):
        return ['queen', 'rook', 'bishop', 'knight']
