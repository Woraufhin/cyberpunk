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
        self.grid = self.get_test_grid()
        self.selected = None
        self.console = None
        self.draw_grid()
        self.draw_armies()

    def update(self):
        self.draw_selected()

    def get_king(self, color: Color):
        uid = 100 + Color(color).value * 10 + PieceType.king.value
        return self.pieces[uid]

    def get_piece(self, color: Color, type: PieceType, num: int):
        uid = num * 100 + Color(color).value * 10 + PieceType(type).value
        try:
            return self.pieces[uid]
        except KeyError:
            return None

    def get_pieces_for_color(self, grid, color: Color):
        pieces = []
        for row in grid:
            for cell in row:
                if cell and self.pieces[cell].color == color:
                    pieces.append(self.pieces[cell])
        return pieces

    def get_possible_moves(self, grid, color: Color):
        pos_moves = []
        for p in self.get_pieces_for_color(grid, color):
            if p.type == PieceType.king:
                for castles in self.get_castle_moves(grid, p):
                    pos_moves.extend(castles)
            for move in p.possible_moves(grid):
                m = (p.pos, move)
                pos_grid = self.simulate_move(grid, m)
                if not self.is_king_checked(pos_grid, color):
                    pos_moves.append(m)
        return pos_moves

    def is_king_checked(self, grid, color):
        rival_color = Color.white if color == Color.black else Color.black
        for p in self.get_pieces_for_color(grid, rival_color):
            for move in p.possible_moves(grid):
                piece_to = self.get_piece_at(move, grid)
                if piece_to and piece_to.type == PieceType.king:
                    return True
        return False

    def get_castle_moves(self, grid, king):
        rook_l, rook_r = self.get_piece(king.color, PieceType.rook, 1), \
                         self.get_piece(king.color, PieceType.rook, 2)
        castle_l, castle_r = king.castle_positions(grid)
        can_left_castle, can_right_castle = True, True
        if not king.moved and not king.is_checked:
            if rook_l and not rook_l.moved and castle_l:
                for move in castle_l:
                    pos_grid = self.simulate_move(grid, (king.pos, move))
                    if self.is_king_checked(pos_grid, king.color):
                        can_left_castle = False
                        break
            else:
                can_left_castle = False
            if rook_r and not rook_r.moved and castle_r:
                for move in castle_r:
                    pos_grid = self.simulate_move(grid, (king.pos, move))
                    if self.is_king_checked(pos_grid, king.color):
                        can_right_castle = False
                        break
            else:
                can_right_castle = False
        else:
            can_left_castle, can_right_castle = False, False

        return [
            list(map(lambda x: (king.pos, x), castle_l)) if can_left_castle else [],
            list(map(lambda x: (king.pos, x), castle_r)) if can_right_castle else []
        ]

    def is_piece_at(self, pos: Coords, grid):
        return True if grid[pos.row, pos.col] else False

    def get_piece_at(self, pos: Coords, grid, fail_if_no_piece: bool = False):
        if self.is_piece_at(pos, grid):
            return self.pieces[grid[pos.row, pos.col]]
        elif fail_if_no_piece:
            raise NoPieceAtIndex(f'No piece at {pos!r}')
        return None

    def promotions(self, color: Color, grid=None):
        grid = grid if grid else self.grid
        promo_row = 0 if color == Color.white else 7
        for piece in self.get_pieces_for_color(grid, color):
            if piece.type == PieceType.pawn and piece.pos.row == promo_row:
                logger.info('Piece: %r is promoting', piece)
                return piece
        return None

    def handle_promotions(self, pawn, new_piece):
        pass

    def select(self, pos: Coords, player_color: str):
        """ Selects a piece on the board """
        if self.selected is not None:
            self.selected = None
            return pos
        piece = self.get_piece_at(pos, self.grid)
        if piece and piece.color == player_color and \
                self.selected != pos:
            sel = pos
        else:
            sel = None
        self.selected = sel
        return sel

    def is_castling_with_rook(self, piece, to):
        if piece.type == PieceType.king:
            if piece.pos.col - 2 == to.col:
                return self.get_piece(piece.color, PieceType.rook, 1)
            elif piece.pos.col + 2 == to.col:
                return self.get_piece(piece.color, PieceType.rook, 2)
        return None

    def move(self, from_: Coords, to: Coords):
        piece_from = self.get_piece_at(from_, self.grid, fail_if_no_piece=True)
        rook = self.is_castling_with_rook(piece_from, to)
        if rook:
            self._castle_move(king=piece_from, rook=rook, to=to)
        else:
            self._move(from_, to)

    def _castle_move(self, king, rook, to):
        off = -1 if king.pos.col + 2 == to.col else 1
        self.console.log('Castling!')

        # move king
        self.grid[to.row, to.col], self.grid[king.pos.row, king.pos.col] = \
            self.grid[king.pos.row, king.pos.col], 0
        # move rook
        self.grid[to.row, to.col+off], self.grid[rook.pos.row, rook.pos.col] = \
            self.grid[rook.pos.row, rook.pos.col], 0

        # update sprites
        king.pos = to
        rook.pos = Coords(x=to.col+off, y=to.row)

    def _move(self, from_: Coords, to: Coords):
        piece_from = self.get_piece_at(from_, self.grid, fail_if_no_piece=True)
        piece_to = self.get_piece_at(to, self.grid)

        # un check check :D. If king is checked only an attempt at solving it
        # could have been done
        king = self.get_king(piece_from.color)
        if king.is_checked:
            king.is_checked = False

        # update grid first
        self.grid[to.row, to.col], self.grid[from_.row, from_.col] = \
            self.grid[from_.row, from_.col], 0

        # update sprite second
        if piece_to:
            self.sprites.remove(piece_to)
            self.captured.append(self.pieces.pop(piece_to.pid))
        piece_from.pos = to

        # check if movement results in any kind of check
        if self.is_king_checked(self.grid, Color.next(piece_from.color)):
            rival_king = self.get_king(Color.next(piece_from.color))
            rival_king.is_checked = True

        # set moved to true third
        try:
            piece_from.moved = True
        except AttributeError:
            pass

    def px_to_grid(self, pos: Coords):
        coords = (pos - self.rect.topleft) / s.TILESIZE // 2
        return Coords(x=coords.x, y=coords.y)

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
            piece = self.get_piece_at(self.selected, self.grid)
            if piece:
                rects = []
                moves = self.get_possible_moves(self.grid, piece.color)
                for move in moves:
                    from_, to = move
                    if from_ == self.selected:
                        rects.append(pg.Rect(
                            to.x * s.TILESIZE * 2, to.y * s.TILESIZE * 2,
                            s.TILESIZE * 2, s.TILESIZE * 2
                        ))
                sel = pg.Rect(
                    self.selected.x * s.TILESIZE * 2, self.selected.y * s.TILESIZE * 2,
                    s.TILESIZE * 2, s.TILESIZE * 2
                )
                pg.draw.rect(self.image, s.YELLOW, sel)
                for rect in rects:
                    pg.draw.rect(self.image, s.YELLOW, rect, 5)

    def set_console(self, console):
        self.console = console

    @staticmethod
    def simulate_move(grid, move) -> np.array:
        new_grid = np.copy(grid)
        from_, to = move
        new_grid[to.row, to.col], new_grid[from_.row, from_.col] = \
            new_grid[from_.row, from_.col], 0
        return new_grid

    @staticmethod
    def get_new_grid():
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

    @staticmethod
    def get_test_grid():
        return np.array([
            [0, 0, 0, 0, 116, 0, 0, 0],
            [0, 221, 321, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [121, 0, 0, 421, 521, 621, 721, 821],
            [122, 123, 124, 125, 126, 224, 223, 222]
        ])