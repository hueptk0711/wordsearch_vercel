from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from game import Game


class Formatter(ABC):
    @abstractmethod
    def show(self, game: Game, *args, **kwargs) -> str:
        """Return a string representation of the game."""

    @abstractmethod
    def save(
        self,
        game: Game,
        path: str | Path,
        format: str = "PDF",
        solution: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        """Save the current puzzle to a file."""
