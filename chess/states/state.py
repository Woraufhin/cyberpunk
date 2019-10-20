import pygame as pg

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Union, Type, ClassVar, List, Callable

import chess.settings as s


@dataclass
class State(metaclass=ABCMeta):
    """ Finite state machine """
    next: ClassVar[Union[None, str]] = None
    sprites: Type['pg.sprite.RenderUpdates'] = field(
        default_factory=pg.sprite.RenderUpdates
    )
    start_time: float = 0.0
    current_time: float = 0.0
    debug_draws: Union[None, List[Callable]] = None
    done: bool = False
    quit: bool = False
    debug: bool = False
    previous: Union[None, str] = None
    persist: dict = field(default_factory=dict)

    @abstractmethod
    def new(self, config=None):
        pass

    def events(self, events: list):
        """ Process events """
        pass

    def startup(self, current_time, persistent):
        """Add variables passed in persistent to the proper attributes and
        set the start time of the State to the current time."""
        self.persist = persistent
        self.start_time = current_time

    def cleanup(self):
        """Add variables that should persist to the self.persist dictionary.
        Then reset State.done to False."""
        self.done = False
        return self.persist

    def update(self, screen, current_time, dt):
        self.current_time = current_time / 1000
        if self.debug:
            for func in self.debug_draws:
                func(screen)
        else:
            screen.fill(s.BLACK)
        self.sprites.update()
        return self.sprites.draw(screen)

    def toggle_debug(self):
        self.debug = not self.debug
