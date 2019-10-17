import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import ClassVar, Union, List, Dict

import pygame as pg
import settings as s
from chess.states.state import State
from chess.panels.tilemap import Board, Grid
from chess.utils.coords import Coords
from chess.player import PlayerFactory
from chess.pieces import Color
from chess.panels.console import Console


vec = pg.math.Vector2
logger = logging.getLogger(Path(__file__).stem)


@dataclass
class Game(State):

    next: ClassVar[Union[None, str]] = None
    board: Union[None, 'Board'] = None
    grid: Union[None, 'Grid'] = None
    panels: List['pg.sprite.Sprite'] = field(default_factory=list)
    players: Dict['Color', 'chess.player.Player'] = field(default_factory=dict)
    turn: Union[None, 'Color'] = None
    moves: int = 0
    config: dict = field(default_factory=dict)

    def __post_init__(self):
        self.debug_draws = [
            self.draw_grid
        ]

    def new(self, config):
        # initialize all variables and do all the setup for a new game
        self.board = Board(
            sprite_group=self.sprites,
            pos=Coords(x=1, y=1),
            size=Coords(x=18, y=18)
        )
        self.grid = Grid(
            sprite_group=self.sprites,
            pos=self.board.pos
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
        self.players = {k: PlayerFactory.make(name=v)(k) for k, v in config['player'].items()}
        self.turn = Color.white

    def startup(self, current_time, persist):
        self.new(config=persist)

    def draw_grid(self, screen):
        for x in range(0, s.WIDTH, s.TILESIZE):
            pg.draw.line(screen, s.LIGHTGREY, (x, 0), (x, s.HEIGHT))
        for y in range(0, s.HEIGHT, s.TILESIZE):
            pg.draw.line(screen, s.LIGHTGREY, (0, y), (s.WIDTH, y))
        for piece in self.grid.piece_sprites:
            pg.draw.rect(self.grid.image, s.RED, piece.rect, 1)

    def act_event(self, event):
        turn_over = False
        grid_click_pos = None
        # catch all events here
        if event.type == pg.KEYDOWN:
            logger.debug('Key pressed: %s', event.unicode)
            if event.key == pg.K_d:
                self.debug = not self.debug
        if event.type == pg.MOUSEBUTTONUP and \
                self.grid.rect.collidepoint(event.pos):
            grid_click_pos = event.pos

        if self.players[self.turn].type == 'human' and grid_click_pos is not None:
            move = self.players[self.turn].move(grid_click_pos, self.grid)
            if move:
                self.log_move(move)
                turn_over = True
        if turn_over:
            self.turn_over()

    def act(self):
        turn_over = False
        if self.players[self.turn].type == 'machine':
            move = self.players[self.turn].move(self.grid)
            if move:
                self.log_move(move)
                turn_over = True
        if turn_over:
            self.turn_over()

    def log_move(self, move):
        self.moves += 1
        self.move.log(f'[{self.moves:03}]')
        self.move.log(str(move))
        self.move.log('')

    def turn_over(self):
        if self.turn == Color.white:
            self.turn = Color.black
        else:
            self.turn = Color.white
