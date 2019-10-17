import logging
from pathlib import Path

import pygame as pg
import settings as s


vec = pg.math.Vector2
logger = logging.getLogger(Path(__file__).stem)


class MovePanel(pg.sprite.Sprite):

    def __init__(self, game, pos):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.image = pg.Surface((s.TILESIZE * 9 * 2, s.TILESIZE * 9 * 2))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.x = self.pos.x
        self.y = self.pos.y
        self.rect.x = self.x * s.TILESIZE
        self.rect.y = self.y * s.TILESIZE