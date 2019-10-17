import pygame as pg


class Coords(pg.math.Vector2):
    @property
    def row(self):
        return self.y

    @property
    def col(self):
        return self.x
