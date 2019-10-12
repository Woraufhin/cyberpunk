import logging
from pathlib import Path

import pygame as pg
import numpy as np

import settings as s


logger = logging.getLogger(Path(__file__).stem)


class Map(pg.sprite.Sprite):

    def __init__(self, game, pos):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.image = pg.Surface((s.TILESIZE * 8, s.TILESIZE * 8))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.x = self.pos.x
        self.y = self.pos.y
        self.rect.x = self.x * s.TILESIZE
        self.rect.y = self.y * s.TILESIZE
        self.grid = np.empty(shape=[8, 8])
        self.draw_grid()

    def draw_grid(self):
        for i, row in enumerate(self.grid):
            color = s.WHITE
            if i % 2 == 0:
                color = s.BLACK
            for j, _ in enumerate(row):
                if color == s.WHITE:
                    color = s.BLACK
                else:
                    color = s.WHITE
                rect = pg.Rect(
                    j * s.TILESIZE, i * s.TILESIZE,
                    s.TILESIZE, s.TILESIZE
                )
                pg.draw.rect(self.image, color, rect)

    def update(self):
        # update board state
        pass