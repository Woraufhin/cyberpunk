import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import ClassVar, Union, List, Dict

import pygame as pg

import chess.settings as s
from chess.states.state import State
from chess.panels.game.wood import Wood
from chess.panels.game.board import Board
from chess.panels.game.promotion import Promotion, Backdrop
from chess.utils.coords import Coords
from chess.player import PlayerFactory
from chess.pieces import Color
from chess.panels.console import Console
from chess.utils.typewriter import TypewriterConfig


logger = logging.getLogger(Path(__file__).stem)


@dataclass
class Game(State):

    next: ClassVar[Union[None, str]] = None
    wood: Union[None, Wood] = None
    board: Union[None, Board] = None
    promotion_sprites: pg.sprite.RenderUpdates = field(
        default_factory=pg.sprite.RenderUpdates
    )
    promoting: bool = False
    players: Dict[Color, 'chess.player.Player'] = field(default_factory=dict)
    turn: Union[None, Color] = None
    moves: int = 0
    config: dict = field(default_factory=dict)
    last_call: int = 0

    def __post_init__(self):
        self.debug_draws = [
            self.draw_grid
        ]

    def new(self, config=None):
        # initialize all variables and do all the setup for a new game
        self.wood = Wood(
            sprite_group=self.sprites,
            pos=Coords(x=1, y=1),
            size=Coords(x=18, y=18)
        )
        self.board = Board(
            sprite_group=self.sprites,
            pos=self.wood.pos
        )
        self.move = Console(
                sprite_group=self.sprites,
                title='MOVE',
                pos=Coords(x=20, y=1),
                size=Coords(x=11, y=10)
        )
        self.console = Console(
                sprite_group=self.sprites,
                pos=Coords(x=20, y=12),
                size=Coords(x=11, y=11)
        )
        self.backdrop = Backdrop(
            sprite_group=self.promotion_sprites,
            pos=Coords(x=0, y=0),
            size=Coords(x=s.GRIDWIDTH, y=s.GRIDHEIGHT)
        )
        self.promotion = Promotion(
            sprite_group=self.promotion_sprites,
            pos=Coords(x=6, y=7),
            size=Coords(x=6, y=6),
            color=s.WHITE,
            parent_color=s.DARKGREY,
            margin=6,
            frame_offset=s.TILESIZE,
            tp_config=TypewriterConfig(
                padding=5,
                size=22,
                color=s.DARKGREEN,
                surface_color=s.DARKGREY,
                pos='midtop'
            )
        )
        self.board.set_console(self.console)
        self.players = {k: PlayerFactory.make(name=v)(k) for k, v in config['player'].items()}
        self.turn = Color.white

    def update(self, screen, current_time, dt):
        self.current_time = current_time / 1000
        if self.debug:
            for func in self.debug_draws:
                func(screen)
        else:
            screen.fill(s.BLACK)
        self.sprites.update()
        rects = self.sprites.draw(screen)
        if self.promoting:
            self.promotion_sprites.update()
            rects.extend(self.promotion_sprites.draw(screen))
        return rects

    def startup(self, current_time, persist):
        self.new(config=persist)

    def draw_grid(self, screen):
        for x in range(0, s.WIDTH, s.TILESIZE):
            pg.draw.line(screen, s.LIGHTGREY, (x, 0), (x, s.HEIGHT))
        for y in range(0, s.HEIGHT, s.TILESIZE):
            pg.draw.line(screen, s.LIGHTGREY, (0, y), (s.WIDTH, y))
        for piece in self.board.piece_sprites:
            pg.draw.rect(self.board.image, s.RED, piece.rect, 1)

    def events(self, events):
        if self.check_mate():
            self.console.log(f'Check mate! WINNER: {Color.next(self.turn)}')
        grid_click_pos = None

        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_d:
                    self.debug = not self.debug
            if event.type == pg.MOUSEBUTTONUP and not self.promoting and \
                    self.board.rect.collidepoint(event.pos):
                logger.info('clicking grid')
                grid_click_pos = event.pos
            if event.type == pg.MOUSEBUTTONUP and self.promoting and \
                    self.promotion.rect.collidepoint(event.pos):
                logger.info('clicking promotion')

        # if it's a "human" turn, then check if she has clicked on the board
        #     if she did, then proceed with human turn
        # else it's an AI, so just move.
        move = None
        if self.players[self.turn].type == 'human' \
                and grid_click_pos is not None:
            move = self.players[self.turn].move(
                self.board,
                self.board.px_to_grid(
                    Coords(x=grid_click_pos[0], y=grid_click_pos[1])
                )
            )
        elif self.players[self.turn].type == 'machine':
            move = self.players[self.turn].move(self.board, None)

        if self.board.promotions(self.turn):
            logger.info('Setting self.promoting = True')
            self.promoting = True

        if move:
            self.log_move(move)
            self.turn = Color.next(self.turn)

    def log_move(self, move):
        king = self.board.get_king(Color.next(self.turn))
        self.moves += 1
        self.move.log(f'[{self.moves:03}]')
        msg = str(move)
        if king.is_checked:
            msg += ' check!'
        self.move.log(msg)
        self.move.log('')

    def check_mate(self):
        king = self.board.get_king(self.turn)
        return king.is_checked and not \
            self.board.get_possible_moves(self.board.grid, self.turn)
