import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Type, ClassVar, Union

import pygame as pg

import chess.settings as s
from chess.utils.coords import Coords
from chess.utils.typewriter import TypewriterConfig, Typewriter


logger = logging.getLogger(Path(__file__).stem)


@dataclass(eq=False)
class Title(pg.sprite.Sprite):
    sprite_group: Type['pg.sprite.Group']
    pos: 'Coords'
    size: 'Coords'
    tp_config: 'TypewriterConfig' = TypewriterConfig(
        size=72,
        pos='center'
    )
    title: str = 'AI Wars'

    def __post_init__(self):
        super().__init__(self.sprite_group)
        self.image = pg.Surface((
            s.TILESIZE * self.size.x,
            s.TILESIZE * self.size.y
        ))
        self.image.fill(s.DARKGREY)
        self.rect = self.image.get_rect()
        self.x = self.pos.x
        self.y = self.pos.y
        self.rect.midtop = (self.x * s.TILESIZE, self.y * s.TILESIZE)
        self.title_writer = Typewriter(
            surface=self.image,
            config=self.tp_config
        )
        self.draw_pixel_art()
        self.draw_title()

    def draw_title(self):
        if self.title:
            self.title_writer.type(self.title)

    def draw_pixel_art(self):
        px = s.TILESIZE / 4
        pg.draw.rect(self.image, s.BLACK, (0, 0, px, px))
        pg.draw.rect(self.image, s.BLACK, (0, self.image.get_height() - px, px, px))
        pg.draw.rect(self.image, s.BLACK, (self.image.get_width() - px, self.image.get_height() - px, px, px))
        pg.draw.rect(self.image, s.BLACK, (self.image.get_width() - px, 0, px, px))
