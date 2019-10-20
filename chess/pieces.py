import sys
import logging
from pathlib import PurePath, Path
from collections import namedtuple
from itertools import chain
from enum import Enum

import pygame as pg
import numpy as np

import chess.settings as s
from chess.utils.coords import Coords


logger = logging.getLogger(Path(__file__).stem)
PieceId = namedtuple('PieceId', ['num', 'color', 'type'])
Offsets = namedtuple('Offsets', ['up', 'down', 'left', 'right'], defaults=[0, 0, 0, 0])


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
        return class_(pid.num, pid.color, pos)


class Piece(pg.sprite.Sprite):
    def __init__(self, type, pid, color, pos):
        super().__init__()
        self.pid = pid
        self.type = type
        self.color = color
        self.move_offset = None
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.pos = pos
        # noinspection PyTypeChecker
        center = self.pos * s.TILESIZE * 2 + (s.TILESIZE, s.TILESIZE)
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
        center = self.pos * s.TILESIZE * 2 + Coords(x=s.TILESIZE, y=s.TILESIZE) * 3
        self.rect.center = (center.x, center.y)

    def possible_moves(self, grid):
        pass

    def get_offsets(self, size):
        off = [-1, size, -1, size]
        if self.move_offset:
            off = self.move_offset
            off = [
                max(-1, self.row - off.up - 1),
                min(8, self.row + off.down + 1),
                max(-1, self.col - off.left - 1),
                min(8, self.col + off.right + 1)
            ]
        return Offsets(*off)

    def diagonals(self, x, y, size):
        off = self.get_offsets(size)
        return [
            zip(range(x - 1, off.up, -1), range(y - 1, off.left, -1)),
            zip(range(x - 1, off.up, -1), range(y + 1, off.right, 1)),
            zip(range(x + 1, off.down, 1), range(y + 1, off.right, 1)),
            zip(range(x + 1, off.down, 1), range(y - 1, off.left, -1))
        ]

    def verticals(self, x, y, size):
        off = self.get_offsets(size)

        up = range(x-1, off.up, -1)
        down = range(x+1, off.down, 1)
        left = range(y-1, off.left, -1)
        right = range(y+1, off.right, 1)

        return [
            zip(up, [y] * len(up)),
            zip(down, [y] * len(down)),
            zip([x] * len(left), left),
            zip([x] * len(right), right)
        ]

    def clear_diagonals(self, grid):
        """ Get free diagonals within offset """
        moves = []
        for diag in self.diagonals(self.row, self.col, 8):
            for coords in diag:
                if grid[coords]:
                    piece = PieceId(*[int(e) for e in str(grid[coords])])
                    if Color(piece.color) != self.color:
                        moves.append(Coords(x=coords[1], y=coords[0]))
                    break
                else:
                    moves.append(Coords(x=coords[1], y=coords[0]))
        return moves

    def clear_verticals(self, grid, can_capture=True):
        """ Get free verticals within offset """
        moves = []
        for vert in self.verticals(self.row, self.col, 8):
            for coords in vert:
                if grid[coords]:
                    piece = PieceId(*[int(e) for e in str(grid[coords])])
                    if can_capture and Color(piece.color) != self.color:
                        moves.append(Coords(x=coords[1], y=coords[0]))
                    break
                else:
                    moves.append(Coords(x=coords[1], y=coords[0]))
        return moves

    @property
    def row(self):
        return int(self.pos.y)

    @property
    def col(self):
        return int(self.pos.x)


class King(Piece):
    def __init__(self, pid, color, pos):
        super().__init__(PieceType.king, pid, color, pos)
        self.moved = False
        self.move_offset = Offsets(1, 1, 1, 1)

    def possible_moves(self, grid):
        return chain.from_iterable([
            self.clear_diagonals(grid),
            self.clear_verticals(grid)
        ])


class Queen(Piece):
    def __init__(self, pid, color, pos):
        super().__init__(PieceType.queen, pid, color, pos)

    def possible_moves(self, grid):
        return chain.from_iterable([
            self.clear_diagonals(grid),
            self.clear_verticals(grid)
        ])


class Rook(Piece):
    def __init__(self, pid, color, pos):
        super().__init__(PieceType.rook, pid, color, pos)
        self.moved = False

    def possible_moves(self, grid):
        return self.clear_verticals(grid)


class Knight(Piece):
    def __init__(self, pid, color, pos):
        super().__init__(PieceType.knight, pid, color, pos)

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
    def __init__(self, pid, color, pos):
        super().__init__(PieceType.bishop, pid, color, pos)

    def possible_moves(self, grid):
        return self.clear_diagonals(grid)


class Pawn(Piece):
    def __init__(self, pid, color, pos):
        super().__init__(PieceType.pawn, pid, color, pos)
        self.moved = False
        self.move_offset = Offsets(
            up=-1 if color == Color.black else 1,
            down=-1 if color == Color.white else 1,
            left=1,
            right=1
        )

    def possible_moves(self, grid):
        moves = []
        for move in self.clear_diagonals(grid):
            # only move diagonally if there's an enemy piece.
            # due to logic in clear_diagonals there can only
            # be enemy pieces
            if grid[move.row, move.col]:
                moves.append(move)

        for move in self.clear_verticals(grid, can_capture=False):
            # only allow y-axis movement
            if move.col == self.col:
                moves.append(move)

        if not self.moved:
            # if pawn hasn't moved yet, then it gets a POWA MOVE
            # if no one is there
            powa_move = Coords(
                x=self.col,
                y=self.row + 2 if self.color == Color.black else self.row - 2
            )
            if powa_move.row < 0 or powa_move.row > 7:
                # TODO
                logger.warning('Reaching edge of board, should promote')
            elif not grid[powa_move.row, powa_move.col]:
                moves.append(powa_move)

        return moves
