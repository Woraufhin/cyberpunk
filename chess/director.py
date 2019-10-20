import logging
from pathlib import Path
from dataclasses import dataclass, field

import pygame as pg


logger = logging.getLogger(Path(__file__).stem)


@dataclass
class Director:
    """ Control class for entire project. Contains the game loop, and contains
    the event_loop which passes events to States as needed. Logic for flipping
    states is also found here. """
    caption: str
    done: bool = field(default=False, init=False)  # to check if STATE is done and we need to change it to state.next
    clock: 'pg.time.Clock' = field(default=pg.time.Clock(), init=False)
    fps: float = 30.0
    show_fps: bool = field(default=True, init=False)
    current_time: float = field(default=0.0, init=False)
    state_dict: dict = field(default_factory=dict, init=False)
    state_name: str = field(default=None, init=False)
    state: 'chess.states.state.State' = field(default=None, init=False)

    def __post_init__(self):
        # I don't know why I can't make it a default with init=False ...
        self.screen = pg.display.get_surface()

    def setup_states(self, state_dict, start_state):
        """ Given a dictionary of States and a State to start in,
        builds the self.state_dict. """
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self, dt):
        """ Checks if a state is done or has called for a game quit.
        State is flipped if necessary and State.update is called. """
        self.current_time = pg.time.get_ticks()
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        rects = self.state.update(self.screen, self.current_time, dt)
        pg.display.update(rects)

    def flip_state(self):
        """ When a State changes to done necessary startup and cleanup functions
        are called and the current State is changed. """
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)
        self.state.previous = previous

    def event_loop(self):
        """ Process all events and pass them down to current State.  The f5 key
        globally turns on/off the display of FPS in the caption """
        if pg.event.get(eventtype=pg.QUIT):
            self.done = True
        elif pg.event.get(eventtype=[pg.K_F5]):
            # FIXME
            self.toggle_show_fps()
        # deliver rest of events to the states
        self.state.events(pg.event.get())

    def toggle_show_fps(self):
        """ Press f5 to turn on/off displaying the framerate in the caption. """
        self.show_fps = not self.show_fps
        if not self.show_fps:
            pg.display.set_caption(self.caption)

    def main(self):
        """ Main loop for entire program. """
        while not self.done:
            time_delta = self.clock.tick(self.fps) / 1000.0
            self.event_loop()
            self.update(time_delta)
            pg.display.update()
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)
