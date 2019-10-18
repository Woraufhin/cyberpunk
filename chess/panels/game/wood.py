import logging
from pathlib import Path
from dataclasses import dataclass

import pygame as pg

import chess.settings as s
from chess.utils.coords import Coords
from chess.utils.typewriter import TypewriterConfig, Typewriter
from chess.panels.panel import Panel


logger = logging.getLogger(Path(__file__).stem)


@dataclass(eq=False)
class Wood(Panel):

    def __post_init__(self):
        super().__post_init__()
        self.draw_margin()
        self.draw_legend()

    def draw_legend(self):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        config = TypewriterConfig(
            size=22,
            color=s.WHITE,
            padding=10,
            surface_color=s.DARKGREY
        )
        tp = Typewriter(
            surface=self.image,
            config=config
        )
        for i, l in enumerate(letters, start=1):
            num_w, num_h = tp.get_text_size(str(i))
            l_w, l_h = tp.get_text_size(l)
            tp.type(
                text=str(i),
                coords=Coords(
                    x=s.TILESIZE // 2 - num_w // 2,
                    y=s.TILESIZE * 2 * i - num_h // 2
                )
            )
            tp.type(
                text=l,
                coords=Coords(
                    x=i * s.TILESIZE * 2 - l_w // 2,
                    y=self.image.get_height() - s.TILESIZE + l_h // 4
                )
            )

    def draw_margin(self):
        m_px = 4
        margin = pg.Rect(
            s.TILESIZE - m_px, s.TILESIZE - m_px,
            2 * (s.TILESIZE * 8 + m_px), 2 * (s.TILESIZE * 8 + m_px)
        )
        pg.draw.rect(self.image, s.GREEN, margin)
