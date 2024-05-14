from myproject.word_generator.utils import find_bounding_box


class MaskNotGenerated(Exception):
    pass


class Mask:

    ACTIVE = "*"
    INACTIVE = "#"
    METHODS = [1, 2, 3]

    def __init__(
        self,
        points: list[tuple[int, int]] | None = None,
        method: int = 1,
        static: bool = True,
    ) -> None:
        self.points = points if points else []
        self.method = method
        self.static = static
        self._puzzle_size: int = 0
        self._mask: list[list[str]] = []

    @property
    def mask(self) -> list[list[str]]:
        """Mask as a 2-D array (list[list[str]])."""
        return self._mask

    @property
    def method(self) -> int:
        """Mask method."""
        return self._method

    @method.setter
    def method(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Must be an integer.")
        if isinstance(value, int) and value not in Mask.METHODS:
            raise ValueError(f"Must be one of {Mask.METHODS}")
        self._method = value

    @property
    def static(self) -> int:
        """Mask static reapplication."""
        return self._static

    @static.setter
    def static(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("Must be a boolean value.")
        self._static = value

    @property
    def puzzle_size(self) -> int:
        return self._puzzle_size

    @puzzle_size.setter
    def puzzle_size(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Must be an integer.")
        self._puzzle_size = value
        if not self.static:
            self.reset_points()

    @property
    def bounding_box(self) -> tuple[tuple[int, int], tuple[int, int]] | None:
        if not self.points:
            return None
        min_x, min_y = self.points[0]
        max_x, max_y = self.points[0]
        for x, y in self.points:
            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y
        return ((min_x, min_y), (max_x, max_y))

    @staticmethod
    def build_mask(size: int, char: str) -> list[list[str]]:
        return [[char] * size for _ in range(size)]

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        self._draw()

    def _draw(self) -> None:
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "Please use `object.generate()` before calling `object.show()`."
            )
        pass

    def show(self, active_only: bool = False) -> None:
        if not self.puzzle_size or not self.bounding_box:
            raise MaskNotGenerated(
                "Please use `object.generate()` before calling `object.show()`."
            )
        if active_only:
            ((min_x, min_y), (max_x, max_y)) = find_bounding_box(
                self._mask, self.ACTIVE
            )
        else:
            ((min_x, min_y), (max_x, max_y)) = (
                (0, 0),
                (self.puzzle_size, self.puzzle_size),
            )
        for r in self.mask[min_y : max_y + 1]:
            if active_only:
                r = [c if c == self.ACTIVE else " " for c in r]
            print(" ".join(r[min_x : max_x + 1]))

    def invert(self) -> None:
        """Invert the mask. Has no effect on the mask `method`."""
        self._mask = [
            [self.ACTIVE if c == self.INACTIVE else self.INACTIVE for c in row]
            for row in self.mask
        ]

    def flip_horizontal(self) -> None:
        """Flip mask along the vertical axis (left to right)."""
        self._mask = [r[::-1] for r in self.mask]

    def flip_vertical(self) -> None:
        """Flip mask along the horizontal axis (top to bottom)."""
        self._mask = self.mask[::-1]

    def transpose(self) -> None:
        """Reverse/permute the axes of the mask."""
        self._mask = list(map(list, zip(*self.mask)))

    def reset_points(self) -> None:
        """Reset all mask coordinate points."""
        self.points = []


class CompoundMask(Mask):

    def __init__(
        self, masks: list[Mask] | None = None, method: int = 1, static: bool = True
    ) -> None:
        super().__init__(method=method, static=static)
        self.masks = masks if masks else []

    @property
    def bounding_box(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return find_bounding_box(self._mask, self.ACTIVE)

    def add_mask(self, mask: Mask) -> None:
        self.masks.append(mask)

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.ACTIVE)
        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)

    def _apply_mask(self, mask: Mask) -> None:
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "Please use `object.generate()` before calling `object.show()`."
            )
        for y in range(self.puzzle_size):
            for x in range(self.puzzle_size):
                if mask.method == 1:
                    if (
                        mask.mask[y][x] == self.ACTIVE
                        and self.mask[y][x] == self.ACTIVE
                    ):
                        self.mask[y][x] = self.ACTIVE
                    else:
                        self.mask[y][x] = self.INACTIVE
                elif mask.method == 2:
                    if mask.mask[y][x] == self.ACTIVE:
                        self.mask[y][x] = self.ACTIVE
                else:
                    if mask.mask[y][x] == self.ACTIVE:
                        self.mask[y][x] = self.INACTIVE

