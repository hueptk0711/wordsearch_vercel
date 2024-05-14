from pathlib import Path

from PIL import Image, ImageChops

from myproject.word_generator.utils import in_bounds
from myproject.word_generator.mask import Mask, MaskNotGenerated


class ContrastError(Exception):
    pass


class Bitmap(Mask):
    def __init__(
        self,
        points: list[tuple[int, int]] | None = None,
        method: int = 1,
        static: bool = True,
    ) -> None:

        super().__init__(points=points, method=method, static=static)

    def _draw(self) -> None:
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `.generate()` method."
            )
        for x, y in self.points:
            if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                self._mask[y][x] = self.ACTIVE


class BitmapImage(Bitmap):
    threshold = 200  # normalization contrast point

    def __init__(self, fp: str | Path, method: int = 1, static: bool = False) -> None:
        
        super().__init__(method=method, static=static)
        self.fp = fp

    def generate(self, puzzle_size: int) -> None:
        """Generate a new mask at `puzzle_size` from a raster image."""
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        img = Image.open(self.fp, formats=("BMP", "JPEG", "PNG"))
        self.points = BitmapImage.process_image(
            img, self.puzzle_size, BitmapImage.threshold
        )
        if not self.points:
            raise ContrastError("The provided image lacked enough contrast.")
        self._draw()

    @staticmethod
    def process_image(
        image: Image.Image, size: int, threshold: int = 200
    ) -> list[tuple[int, int]]:
        image = image.convert("L").point(
            lambda px: 255 if px > BitmapImage.threshold else 0, mode="1"
        )
        diff = ImageChops.difference(image, Image.new("L", image.size, (255)))
        bbox = diff.getbbox()
        image = image.crop(bbox)
        image.thumbnail((size, size), resample=0)
        w, _ = image.size
        return [
            (0 if i == 0 else i % w, i // w)
            for i, px in enumerate(image.getdata())
            if px <= threshold
        ]