from __future__ import annotations

from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:  # pragma: no cover
    from .game import Game, Puzzle


Fit: TypeAlias = tuple[str, list[tuple[int, int]]]
Fits: TypeAlias = list[tuple[str, list[tuple[int, int]]]]


class WordFitError(Exception):
    pass


def retry(retries: int = 1000):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempt += 1
            return

        return wrapper

    return decorator


class Generator(ABC):
    @abstractmethod
    def generate(self, game: Game) -> Puzzle:
        """Generate a puzzle."""
