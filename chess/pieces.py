import sys
import logging
from pathlib import PurePath, Path
from collections import namedtuple
from itertools import chain
from enum import Enum

import pygame as pg
import numpy as np

import settings as s
from chess.utils.coords import Coords


vec = pg.math.Vector2
logger = logging.getLogger(Path(__file__).stem)
PieceId = namedtuple('PieceId', ['num', 'color', 'type'])


class PieceType(Enum):
    pawn = 1
    rook = 2
    knight = 3
    bishop = 4
    queen = 5
    king = 6


class Color(Enum):
    black = 1
    white = 2


class PieceFactory:
    @staticmethod
    def make(pid, pos):
        class_ = getattr(
            sys.modules[__name__], pid.type.name.capitalize()
        )
        return class_(pid.color, pos)


class Piece(pg.sprite.Sprite):
    def __init__(self, type, color, pos):
        super().__init__()
        self.type = type
        self.color = color
        self.move_offset = None
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.pos = pos
        # noinspection PyTypeChecker
        center = self.pos * s.TILESIZE * 2 + (s.TILESIZE, s.TILESIZE)
        logging.info('Creating %s at %r | %r', type.name, center, pos)
        self.rect.center = (center.x, center.y)

    def load_image(self):
        """ Load sprite for each piece and transform it accordingly"""
        img = pg.image.load(
            str(PurePath(s.SPRITE_FOLDER, f'{self.color.name}_{self.type.name}.png'))
        ).convert_alpha()
        img = pg.transform.scale(img, (int(s.TILESIZE * 1.5), int(s.TILESIZE * 1.5)))
        return img

    def update(self):
        # noinspection PyTypeChecker
        center = self.pos * s.TILESIZE * 2 + (s.TILESIZE, s.TILESIZE)
        self.rect.center = (center.x, center.y)

    def possible_moves(self, grid):
        pass

    def get_offsets(self, size):
        Offsets = namedtuple('Offsets', ['up', 'down', 'left', 'right'])
        off = [-1, size, -1, size]
        if self.move_offset:
            off = [
                max(-1, self.row - self.move_offset - 1),
                min(8, self.row + self.move_offset + 1),
                max(-1, self.col - self.move_offset - 1),
                min(8, self.col + self.move_offset + 1)
            ]
        return Offsets(*off)

    def diagonals(self, x, y, size):
        off = self.get_offsets(size)
        moves = [
            zip(range(x - 1, off.up, -1), range(y - 1, off.left, -1)),
            zip(range(x - 1, off.up, -1), range(y + 1, off.right, 1))
        ]
        if not self.is_white_pawn():
            moves.append(zip(range(x + 1, off.down, 1), range(y + 1, off.right, 1)))
            moves.append(zip(range(x + 1, off.down, 1), range(y - 1, off.left, -1)))
        return moves

    def verticals(self, x, y, size):
        off = self.get_offsets(size)
        moves = []

        up = range(x-1, off.up, -1)
        down = range(x+1, off.down, 1)
        left = range(y-1, off.left, -1)
        right = range(y+1, off.right, 1)

        if self.is_white_pawn():
            moves.append(zip(up, [y] * len(up)))
        else:
            moves.append(zip(down, [y] * len(down)))
        if self.type != PieceType.pawn:
            moves.append(zip(up, [y] * len(up)))
            moves.append(zip([x] * len(left), left))
            moves.append(zip([x] * len(right), right))
        return moves

    def allowed_diagonals(self, grid):
        moves = []
        diags = self.diagonals(self.row, self.col, 8)
        for diag in diags:
            for coords in diag:
                if grid[coords]:
                    piece = PieceId(*[int(e) for e in str(grid[coords])])
                    if Color(piece.color) != self.color:
                        moves.append(Coords(x=coords[1], y=coords[0]))
                    break
                elif self.type != PieceType.pawn:
                    moves.append(Coords(x=coords[1], y=coords[0]))
        return moves

    def allowed_verticals(self, grid):
        moves = []
        verts = self.verticals(self.row, self.col, 8)
        for vert in verts:
            for coords in vert:
                if grid[coords]:
                    piece = PieceId(*[int(e) for e in str(grid[coords])])
                    if Color(piece.color) != self.color:
                        moves.append(Coords(x=coords[1], y=coords[0]))
                    break
                else:
                    moves.append(Coords(x=coords[1], y=coords[0]))
        return moves

    def is_white_pawn(self):
        return self.type == PieceType.pawn and self.color == Color.white

    @property
    def row(self):
        return int(self.pos.y)

    @property
    def col(self):
        return int(self.pos.x)


class King(Piece):
    def __init__(self, color, pos):
        super().__init__(PieceType.king, color, pos)
        self.move_offset = 1

    def possible_moves(self, grid):
        return chain(
            self.allowed_diagonals(grid),
            self.allowed_verticals(grid)
        )


class Queen(Piece):
    def __init__(self, color, pos):
        super().__init__(PieceType.queen, color, pos)

    def possible_moves(self, grid):
        return chain(
            self.allowed_diagonals(grid),
            self.allowed_verticals(grid)
        )


class Rook(Piece):
    def __init__(self, color, pos):
        super().__init__(PieceType.rook, color, pos)

    def possible_moves(self, grid):
        return self.allowed_verticals(grid)


class Knight(Piece):
    def __init__(self, color, pos):
        super().__init__(PieceType.knight, color, pos)

    def possible_moves(self, grid):
        moves = []
        offset = np.array([[-2, -1], [-2, 1], [2, -1], [2, 1]])
        idx = np.row_stack((offset, offset[:, ::-1])) + (self.row, self.col)
        idxs = idx[~((idx < 0) | (idx > 7)).any(1)]
        for coords in idxs:
            coords = tuple(coords)
            if grid[coords]:
                piece = PieceId(*[int(e) for e in str(grid[coords])])
                if Color(piece.color) != self.color:
                    moves.append(Coords(x=coords[1], y=coords[0]))
            else:
                moves.append(Coords(x=coords[1], y=coords[0]))
        return moves


class Bishop(Piece):
    def __init__(self, color, pos):
        super().__init__(PieceType.bishop, color, pos)

    def possible_moves(self, grid):
        return self.allowed_diagonals(grid)


class Pawn(Piece):
    def __init__(self, color, pos):
        super().__init__(PieceType.pawn, color, pos)
        self.move_offset = 1

    def possible_moves(self, grid):
        return chain(
            self.allowed_diagonals(grid),
            self.allowed_verticals(grid)
        )
