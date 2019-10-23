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
class Panel(pg.sprite.Sprite):
    sprite_group: pg.sprite.Group
    pos: 'Coords'
    size: 'Coords'
    tp_config: 'TypewriterConfig' = TypewriterConfig(
        size=44,
        surface_color=s.DARKGREY,
        pos='midtop'
    )
    title: Union[None, str] = None
    alpha: Union[None, int] = None
    parent_color: tuple = s.BLACK
    color: tuple = s.DARKGREY
    draw_title: bool = True
    draw_px_art: bool = True

    def __post_init__(self):
        super().__init__(self.sprite_group)
        args = [(s.TILESIZE * self.size.x, s.TILESIZE * self.size.y)]
        if self.alpha:
            args.append(pg.SRCALPHA)
        self.image = pg.Surface(*args)
        if self.alpha:
            self.color = (*self.color, self.alpha)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.x = self.pos.x
        self.y = self.pos.y
        self.rect = self.image.get_rect(
            topleft=(
                self.x * s.TILESIZE,
                self.y * s.TILESIZE
            )
        )
        self.title_writer = Typewriter(
            surface=self.image,
            config=self.tp_config
        )
        self.draw_pixel_art()
        self._draw_title()

    def _draw_title(self):
        if self.draw_title and self.title:
            self.title_writer.type(self.title)

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
