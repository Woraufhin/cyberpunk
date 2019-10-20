import logging
from pathlib import Path

import pygame as pg
import numpy as np

import chess.settings as s
from chess.utils.coords import Coords
from chess.pieces import PieceFactory, PieceId, PieceType, Color


logger = logging.getLogger(Path(__file__).stem)


class NoPieceAtIndex(Exception):
    """ Tried to get a non existent piece """


class Board(pg.sprite.Sprite):

    PADDING = s.TILESIZE

    def __init__(self, sprite_group, pos):
        self.sprites = sprite_group
        super().__init__(self.sprites)
        self.pieces = {}
        self.image = pg.Surface((s.TILESIZE * 8 * 2, s.TILESIZE * 8 * 2))
        self.rect = self.image.get_rect(topleft=(
            pos.x * s.TILESIZE + self.PADDING,
            pos.y * s.TILESIZE + self.PADDING
        ))
        self.captured = []
        self.grid = self.get_grid()
        self.selected = None
        self.draw_grid()
        self.draw_armies()

    def update(self):
        self.draw_selected()

    def get_pieces_for_color(self, color: Color):
        return [p for p in self.pieces.values() if p.color == color]

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
                    pid = PieceId(
                        num=cell,
                        color=Color(int(c[-2])),
                        type=PieceType(int(c[-1]))
                    )
                    piece = PieceFactory.make(pid, Coords(x=j, y=i))
                    self.pieces[pid.num] = piece
                    self.sprites.add(piece)

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
                pg.draw.rect(self.image, s.YELLOW, sel)
                for rect in rects:
                    pg.draw.rect(self.image, s.YELLOW, rect, 5)

    def is_piece_at(self, pos: Coords):
        return True if self.grid[pos.row, pos.col] else False

    def get_piece_at(self, pos: Coords, fail_if_no_piece: bool = False):
        if self.is_piece_at(pos):
            return self.pieces[self.grid[pos.row, pos.col]]
        elif fail_if_no_piece:
            raise NoPieceAtIndex(f'No piece at {pos!r}')
        return None

    def select(self, pos: Coords, player_color: str):
        """ Selects a piece on the board """
        if self.selected is not None:
            self.selected = None
            return pos
        piece = self.get_piece_at(pos)
        if piece and piece.color == player_color and \
                self.selected != pos:
            sel = pos
        else:
            sel = None
        self.selected = sel
        return sel

    def move(self, from_: Coords, to: Coords):
        piece_from = self.get_piece_at(from_, fail_if_no_piece=True)
        piece_to = self.get_piece_at(to)

        # update grid first
        self.grid[to.row, to.col], self.grid[from_.row, from_.col] = \
            self.grid[from_.row, from_.col], 0

        # update sprite second
        if piece_to:
            self.sprites.remove(piece_to)
            self.captured.append(self.pieces.pop(piece_to.pid))
        piece_from.pos = to

        # set moved to true third
        try:
            piece_from.moved = True
        except AttributeError:
            pass

    def px_to_grid(self, pos: Coords):
        coords = (pos - self.rect.topleft) / s.TILESIZE // 2
        return Coords(x=coords.x, y=coords.y)

    def erase_selected(self):
        self.selected = None

    @staticmethod
    def get_grid():
        return np.array([
            [112, 113, 114, 115, 116, 214, 213, 212],
            [111, 211, 311, 411, 511, 611, 711, 811],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [121, 221, 321, 421, 521, 621, 721, 821],
            [122, 123, 124, 125, 126, 224, 223, 222]
        ])
