import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Union

import pygame as pg

import chess.settings as s
from chess.states.state import State
from chess.panels.intro.title import Title
from chess.panels.intro.menu import Menu
from chess.panels.console import Console
from chess.utils.coords import Coords
from chess.utils.typewriter import Typewriter, TypewriterConfig, LogType


vec = pg.math.Vector2
logger = logging.getLogger(Path(__file__).stem)


@dataclass
class Intro(State):

    next = 'GAME'
    greet = {
            1: [False, ('[DEBUG] Loading protocol...', LogType.DEBUG)],
            3: [False, (
                '[WARNING] Cannot load "assets/fonts/stolen.ttf". Proceeding with default.',
                LogType.WARNING
            )],
            3.2: [False, (f'[DEBUG] Displaying <State: Intro> interface.', LogType.DEBUG)],
            3.3: [False, ('[DEBUG] Invoke <func: self.say_hi>', LogType.DEBUG)],
            4: [False, ('[INFO] Hello person, I\'m beep boop.',)],
            4.4: [False, ('[DEBUG] Waiting for input...', LogType.DEBUG)]
    }
    title: Union[None, 'Title'] = None
    menu: Union[None, 'Menu'] = None
    console: Union[None, 'Console'] = None
    info_console: Union[None, 'Console'] = None

    def __post_init__(self):
        self.debug_draws = [
            self.draw_grid,
            self.draw_mouse_pos
        ]
        self.new()

    def new(self, config=None):
        self.title = Title(
            sprite_group=self.sprites,
            pos=Coords(x=s.GRIDWIDTH//2, y=1),
            size=Coords(x=16, y=4)
        )
        self.menu = Menu(
            sprite_group=self.sprites,
            pos=Coords(x=s.GRIDWIDTH//2, y=6),
            size=Coords(x=22, y=15)
        )
        self.console = Console(
            sprite_group=self.sprites,
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
            ),
            config=TypewriterConfig(
                surface_color=s.BLACK,
                size=12,
                padding=5
            )
        )
        self.info_console = Console(
            sprite_group=self.sprites,
            pos=Coords(x=s.GRIDWIDTH//2+4, y=7),
            size=Coords(x=6, y=6),
            title='INFO',
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
            ),
            config=TypewriterConfig(
                surface_color=s.BLACK,
                color=s.WHITE,
                size=12,
                padding=5
            )
        )
        self.menu.set_console(self.console)
        self.menu.set_info_console(self.info_console)

    def update(self, screen, current_time, dt):
        self.current_time = current_time / 1000
        if self.debug:
            for func in self.debug_draws:
                func(screen)
        else:
            screen.fill(s.BLACK)
        self.sprites.draw(screen)
        self.sprites.update()
        self.say_hi()

    def say_hi(self):
        for k, v in self.greet.items():
            if not v[0] and k < self.current_time:
                v[0] = True
                self.console.log(*v[1])

    def events(self, events: list):
        action = None
        for event in events:
            if event.type == pg.KEYDOWN and event.key == pg.K_d:
                self.toggle_debug()
            elif event.type == pg.MOUSEBUTTONUP:
                action = self.menu.click(event.pos)
        self.persist = self.menu.config
        if action:
            if action == 'PLAY':
                if self.check():
                    self.next = 'GAME'
                    self.done = True
            elif action == 'QUIT':
                self.quit = True

    def check(self):
        if len(self.persist['player']) != 2:
            self.console.log('[ERROR] You need another player!', LogType.ERROR)
            return False
        return True

    @staticmethod
    def draw_grid(screen):
        for x in range(0, s.WIDTH, s.TILESIZE):
            pg.draw.line(screen, s.LIGHTGREY, (x, 0), (x, s.HEIGHT))
        for y in range(0, s.HEIGHT, s.TILESIZE):
            pg.draw.line(screen, s.LIGHTGREY, (0, y), (s.WIDTH, y))

    def draw_mouse_pos(self, screen):
        mpos = pg.mouse.get_pos()
        coords = Coords(x=s.TILESIZE*3, y=s.TILESIZE)
        follow = pg.Surface((coords.x, coords.y))
        rect = follow.get_rect(topleft=(0, 0))
        tp = Typewriter(follow, TypewriterConfig(size=12, pos='center'))
        tp.type(str(mpos))
        screen.blit(follow, rect)
