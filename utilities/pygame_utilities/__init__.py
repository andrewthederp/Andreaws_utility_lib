import pygame

from .debug_menu import *


class Scheduler:
    def __init__(self):
        self._to_run = []

    def run_in(self, func, *, seconds: int | float):  # use functools.partial to pass in args
        self._to_run.append((func, pygame.time.get_ticks(), seconds))

    def update(self):
        indexes_to_remove = []
        for i, args in enumerate(self._to_run):
            func, start, seconds = args
            if (pygame.time.get_ticks() - start) > seconds * 1000:
                func()
                indexes_to_remove.append(i)

        for index in sorted(indexes_to_remove, reverse=True):
            self._to_run.pop(index)
