import sys
import logging
from pathlib import Path

import pygame as pg
import settings as s
from tilemap import Board, Grid
from utils import draw_text
from player import HumanPlayer, RandomAI
from pieces import Color


vec = pg.math.Vector2
logger = logging.getLogger(Path(__file__).stem)


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((s.WIDTH, s.HEIGHT))
        pg.display.set_caption(s.TITLE)
        self.clock = pg.time.Clock()
        self.debug = False
        self.load_data()

    def load_data(self):
        pass

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.board = Board(
            game=self,
            pos=vec(1, 2)
        )
        self.grid = Grid(
            game=self,
            pos=self.board.pos
        )
        self.players = {
            Color.white: RandomAI(Color.white),
            Color.black: HumanPlayer(Color.black)
        }
        self.turn = Color.white

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(s.FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

    def draw_grid(self):
        for x in range(0, s.WIDTH, s.TILESIZE):
            pg.draw.line(self.screen, s.LIGHTGREY, (x, 0), (x, s.HEIGHT))
        for y in range(0, s.HEIGHT, s.TILESIZE):
            pg.draw.line(self.screen, s.LIGHTGREY, (0, y), (s.WIDTH, y))
        for piece in self.grid.piece_sprites:
            pg.draw.rect(self.grid.image, s.RED, piece.rect, 1)

    def draw(self):
        self.screen.fill(s.BGCOLOR)
        if self.debug:
            self.draw_grid()
        self.all_sprites.draw(self.screen)
        draw_text(
            surf=self.screen,
            text='AI Wars',
            size=64,
            pos=vec(7 * s.TILESIZE, 0)
        )
        pg.display.flip()

    def events(self):
        turn_over = False
        grid_click_pos = None
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                logger.debug('Key pressed: %s', event.unicode)
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_v:
                    self.debug = not self.debug
            if event.type == pg.MOUSEBUTTONUP and \
                    self.grid.rect.collidepoint(event.pos):
                grid_click_pos = event.pos

        if isinstance(self.players[self.turn], HumanPlayer) and grid_click_pos is not None:
            if self.players[self.turn].move(grid_click_pos, self.grid):
                turn_over = True
        elif isinstance(self.players[self.turn], RandomAI):
            if self.players[self.turn].move(self.grid):
                turn_over = True
        if turn_over:
            self.turn_over()

    def turn_over(self):
        if self.turn == Color.white:
            self.turn = Color.black
        else:
            self.turn = Color.white

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
        datefmt='%I:%M:%S %p',
        level=logging.DEBUG
    )

    g = Game()
    g.show_start_screen()
    while True:
        g.new()
        g.run()
        g.show_go_screen()
