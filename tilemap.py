import logging
from pathlib import Path
from collections import defaultdict

import pygame as pg
import numpy as np

import settings as s
from utils import draw_text
from pieces import PieceFactory, PieceId, PieceType, Color

vec = pg.math.Vector2
logger = logging.getLogger(Path(__file__).stem)


class Board(pg.sprite.Sprite):

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
        self.draw_board()
        self.draw_legend()

    def draw_legend(self):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, l in enumerate(letters, start=1):
            draw_text(
                surf=self.image,
                text=str(i),
                size=22,
                pos=vec(5, s.TILESIZE * 2 * i),
                color=s.WHITE
            )
            draw_text(
                surf=self.image,
                text=l,
                size=22,
                pos=vec(i * s.TILESIZE * 2, self.image.get_height() - s.TILESIZE),
                color=s.WHITE
            )

    def draw_board(self):
        # greyboard
        greyboard = pg.Rect(
            0, 0,
            s.TILESIZE * 2 * 9, s.TILESIZE * 2 * 9
        )
        pg.draw.rect(self.image, s.DARKGREY, greyboard)

        # margin
        m_px = 4
        margin = pg.Rect(
            s.TILESIZE - m_px, s.TILESIZE - m_px,
            2 * (s.TILESIZE * 8 + m_px), 2 * (s.TILESIZE * 8 + m_px)
        )
        pg.draw.rect(self.image, s.GREEN, margin)

        # pixel art
        px = s.TILESIZE / 4
        pg.draw.rect(self.image, s.BLACK, (0, 0, px, px))
        pg.draw.rect(self.image, s.BLACK, (0, self.image.get_width() - px, px, px))
        pg.draw.rect(self.image, s.BLACK, (self.image.get_height() - px, self.image.get_width() - px, px, px))
        pg.draw.rect(self.image, s.BLACK, (self.image.get_height() - px, 0, px, px))


class Grid(pg.sprite.Sprite):

    PADDING = s.TILESIZE

    def __init__(self, game, pos):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.piece_sprites = pg.sprite.Group()
        self.pieces = {}
        self.piece_ids = []
        self.image = pg.Surface((s.TILESIZE * 8 * 2, s.TILESIZE * 8 * 2))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.x = self.pos.x
        self.y = self.pos.y
        self.rect.x = self.x * s.TILESIZE + self.PADDING
        self.rect.y = self.y * s.TILESIZE + self.PADDING
        # x1x2x3: unique id
        #    x1: number
        #    x2: team
        #    x3: piece type
        self.grid = np.array([
            [112, 113, 114, 115, 116, 214, 213, 212],
            [111, 211, 311, 411, 511, 611, 711, 811],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [121, 221, 321, 421, 521, 621, 721, 821],
            [122, 123, 124, 125, 126, 224, 223, 222]
        ])
        self.selected = None
        self.draw_grid()
        self.draw_armies()

    @property
    def pawn_lines(self):
        return [1, 6]

    @property
    def white_pieces(self):
        return [self.pieces[p.num] for p in self.piece_ids if p.color == Color.white]

    def px_to_grid(self, pos: pg.math.Vector2):
        return (pos - self.rect.topleft) / s.TILESIZE // 2

    def draw_grid(self):
        for i, row in enumerate(self.grid):
            color = s.LIGHTGREEN
            if i % 2 == 0:
                color = s.DARKGREEN
            for j, _ in enumerate(row):
                if color == s.LIGHTGREEN:
                    color = s.DARKGREEN
                else:
                    color = s.LIGHTGREEN

                rect = pg.Rect(
                    j * s.TILESIZE * 2, i * s.TILESIZE * 2,
                    s.TILESIZE * 2, s.TILESIZE * 2
                )
                pg.draw.rect(self.image, color, rect)

    def draw_armies(self):
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell:
                    c = str(cell)
                    id = PieceId(
                        num=cell,
                        color=Color(int(c[-2])),
                        type=PieceType(int(c[-1]))
                    )
                    piece = PieceFactory.make(id, vec(j, i))
                    self.pieces[id.num] = piece
                    self.piece_ids.append(id)
                    self.piece_sprites.add(piece)

    def draw_selected(self):
        self.draw_grid()
        if self.selected is not None:
            piece = self.get_piece_at(self.selected)
            if piece:
                rects = [pg.Rect(
                    p.x * s.TILESIZE * 2, p.y * s.TILESIZE * 2,
                    s.TILESIZE * 2, s.TILESIZE * 2
                ) for p in piece.possible_moves(self.grid)]
                sel = pg.Rect(
                    self.selected.x * s.TILESIZE * 2, self.selected.y * s.TILESIZE * 2,
                    s.TILESIZE * 2, s.TILESIZE * 2
                )
                pg.draw.rect(self.image, s.WHITE, sel)
                for rect in rects:
                    pg.draw.rect(self.image, s.WHITE, rect, 2)

    def is_piece_at(self, pos: pg.math.Vector2):
        return True if self.grid[int(pos.y), int(pos.x)] else False

    def get_piece_at(self, pos):
        if self.is_piece_at(pos):
            return self.pieces[self.grid[int(pos.y), int(pos.x)]]
        else:
            return None

    def select(self, pos, player_color):
        gpos = self.px_to_grid(vec(*pos))
        if self.selected is not None:
            return gpos
        piece = self.get_piece_at(gpos)
        if piece and piece.color == player_color and \
                self.selected != gpos:
            sel = gpos
        else:
            sel = None
        self.selected = sel
        return sel

    def move(self, from_, to, color):
        piece = self.get_piece_at(from_)
        if (piece.color != color) or \
           (to not in piece.possible_moves(self.grid)):
            logger.debug('Won\'t move: %r, from: %r, to: %r', piece, from_, to)
            self.selected = None
            return False

        self._move(piece, from_, to)
        self.selected = None
        return True

    def _move(self, piece, from_, to):
        # update sprite position and check collision
        piece.pos = to
        piece_at = self.get_piece_at(to)
        if piece_at:
            logger.debug('Player: %r captured: %r', piece.color, piece_at.type)
            self.piece_sprites.remove(piece_at)
        # update grid position
        self.grid[int(to.y), int(to.x)], self.grid[int(from_.y), int(from_.x)] = \
            self.grid[int(from_.y), int(from_.x)], 0
        logger.info('Move: %r, from: %r, to: %r', piece, from_, to)
        logger.info(self.grid)

    def update(self):
        self.draw_selected()
        self.piece_sprites.draw(self.image)
        self.piece_sprites.update()
