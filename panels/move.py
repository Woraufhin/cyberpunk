import logging
from pathlib import Path

import pygame as pg

import settings as s
from utils import draw_text


vec = pg.math.Vector2
logger = logging.getLogger(Path(__file__).stem)


class MovePanel(pg.sprite.Sprite):

    def __init__(self, game, pos):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.image = pg.Surface((s.TILESIZE * 11, s.TILESIZE * 10))
        self.image.fill((s.DARKGREY))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.x = self.pos.x
        self.y = self.pos.y
        self.rect.x = self.x * s.TILESIZE
        self.rect.y = self.y * s.TILESIZE
        self.draw_pixel_art()
        self.draw_legend()

    def draw_legend(self):
        draw_text(
            surf=self.image,
            text='MOVES',
            size=44,
            pos='midtop',
            vpad=10
        )

    def draw_pixel_art(self):
        # greyboard
        # greyboard = pg.Rect(
        #     0, 0,
        #     s.TILESIZE * 2 * 9, s.TILESIZE * 2 * 9
        # )
        # pg.draw.rect(self.image, s.DARKGREY, greyboard)

        # insides
        m_px = 20
        margin = pg.Rect(
            s.TILESIZE - m_px, s.TILESIZE * 2,
            (s.TILESIZE * 9 + m_px * 2), (s.TILESIZE * 7 + m_px)
        )
        pg.draw.rect(self.image, s.BLACK, margin)

        # pixel art
        px = s.TILESIZE / 4
        pg.draw.rect(self.image, s.BLACK, (0, 0, px, px))
        pg.draw.rect(self.image, s.BLACK, (0, self.image.get_height() - px, px, px))
        pg.draw.rect(self.image, s.BLACK, (self.image.get_width() - px, self.image.get_height() - px, px, px))
        pg.draw.rect(self.image, s.BLACK, (self.image.get_width() - px, 0, px, px))