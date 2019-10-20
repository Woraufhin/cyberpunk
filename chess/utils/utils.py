import logging
import operator
from pathlib import Path

import pygame as pg

import chess.settings as s


logger = logging.getLogger(Path(__file__).stem)


class Coords(pg.math.Vector2):
    @property
    def row(self):
        logger.info('here')
        return int(self.y)

    @property
    def col(self):
        return int(self.x)


def draw_text(surf, text, size, pos, color=s.GREEN, vpad=0):
    font = pg.font.Font(s.FONT_PATH, size)
    font.set_bold(2)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()

    h = text_surf.get_height()

    if pos == 'center':
        text_rect.center = surf.get_rect().center
    elif pos == 'midtop':
        tpos = tuple(map(operator.add, surf.get_rect().midtop, (0, vpad)))
        text_rect.midtop = tpos
    else:
        text_rect.topleft = (pos.x, pos.y)
    surf.blit(text_surf, text_rect)
