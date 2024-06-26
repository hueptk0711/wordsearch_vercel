import math

from myproject.word_generator.utils import in_bounds, round_half_up
from myproject.word_generator.mask import Mask, MaskNotGenerated


class Polygon(Mask):
    def __init__(
        self,
        points: list[tuple[int, int]] | None = None,
        method: int = 1,
        static: bool = True,
    ) -> None:
        
        if points and len(points) < 3:
            raise ValueError(
                "Minimum of 3 points (vertices) required to create a Polygon."
            )
        super().__init__(points=points, method=method, static=static)

    @property
    def split_points(self) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        
        left_offset = (
            len(self.points) // 2 + 1
            if len(self.points) % 2 == 0
            else len(self.points) // 2 + 2
        )
        left_side = self.points[0:left_offset]
        right_offset = len(self.points) // 2
        right_side = [self.points[0]] + list(reversed(self.points))[:right_offset]
        return left_side, right_side

    def generate(self, puzzle_size: int) -> None:
        """Generate a new mask at `puzzle_size`."""
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        self._draw()

    def _draw(self) -> None:  # doesn't draw evenly on second half pf point (going up)
        
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            self._connect_points(p1, p2, self.ACTIVE)
        self._fill_shape(self.ACTIVE)

    def _draw_in_halves(self) -> None:
        for points in self.split_points:
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                self._connect_points(p1, p2, self.ACTIVE)
        self._fill_shape(self.ACTIVE)

    def _connect_points(self, p1: tuple[int, int], p2: tuple[int, int], c: str) -> None:
        
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `generate()` method."
            )
        x1, y1 = p1
        x2, y2 = p2
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = -1 if x1 > x2 else 1
        sy = -1 if y1 > y2 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                    self.mask[y][x] = c
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                    self.mask[y][x] = c
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
            if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                self.mask[y][x] = c

    def _fill_shape(self, c: str) -> None:
        """Fill the interior of a polygon using the single character string `c`."""

        def ray_casting(point, polygon):
            
            x, y = point
            ct = 0
            for i in range(len(polygon) - 1):
                x1, y1 = polygon[i]
                x2, y2 = polygon[i + 1]
                if (y < y1) != (y < y2) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                    ct += 1
            return ct % 2 == 1

        if not self.puzzle_size or not self.bounding_box:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `generate()` method."
            )

        # check all points within the polygon bounding box
        bbox = self.bounding_box
        min_x, min_y = bbox[0]
        max_x, max_y = bbox[1]
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                in_polygon = ray_casting((x, y), self.points + [self.points[0]])
                if in_polygon and in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                    self.mask[y][x] = c


class Rectangle(Polygon):
    def __init__(
        self,
        width: int,
        height: int,
        origin: tuple[int, int] | None = None,
        method: int = 1,
        static: bool = True,
    ) -> None:
        originX, originY = origin if origin else (0, 0)
        points = [
            (originX, originY),
            (originX, originY + height - 1),
            (originX + width - 1, originY + height - 1),
            (originX + width - 1, originY),
        ]
        super().__init__(points=points, method=method, static=static)


class RegularPolygon(Polygon):
    def __init__(
        self,
        vertices: int = 3,
        radius: int | None = None,
        center: tuple[int, int] | None = None,
        angle: float = 0.0,
        method: int = 1,
        static: bool = False,
    ) -> None:
        
        if vertices < 3:
            raise ValueError(
                "Minimum of 3 points (vertices) required to create a Polygon."
            )
        super().__init__(method=method, static=static)
        self.vertices = vertices
        self.radius = radius
        self.center = center
        self.angle = angle

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        radius = (
            self.radius
            if self.radius
            else (
                self.puzzle_size // 2 - 1
                if puzzle_size % 2 == 0
                else self.puzzle_size // 2
            )
        )
        self.points = RegularPolygon.calculate_vertices(
            self.vertices,
            radius,
            self.center if self.center else (radius, radius),
            self.angle,
        )
        self._draw()

    @staticmethod
    def calculate_vertices(
        vertices: int,
        radius: int,
        center: tuple[int, int],
        angle: float,
    ):
        points = []
        cx, cy = center
        angle_step = 360.0 / vertices
        angle = angle - 90  # rotated -90 so polygons are oriented North
        for _ in range(vertices):
            x, y = RegularPolygon.cos_sin_from_degrees(angle)
            points.append(
                (
                    int(round_half_up(x * radius + cx)),
                    int(round_half_up(y * radius + cy)),
                )
            )
            angle += angle_step
        return points

    @staticmethod
    def cos_sin_from_degrees(degrees: float) -> tuple[float, float]:
        degrees = degrees % 360.0
        proper_90s = {90.0: (0.0, 1.0), 180.0: (-1.0, 0), 270.0: (0, -1.0)}
        if degrees in proper_90s:
            return proper_90s[degrees]
        rad = math.radians(degrees)
        return math.cos(rad), math.sin(rad)


class Star(Polygon):

    def __init__(
        self,
        outer_vertices: int = 5,
        outer_radius: int | None = None,
        inner_radius: int | None = None,
        center: tuple[int, int] | None = None,
        angle: float = 0.0,
        method: int = 1,
        static: bool = False,
    ) -> None:
        
        if outer_vertices < 3:
            raise ValueError(
                "Minimum of 3 points (vertices) required to create a Polygon."
            )
        super().__init__(method=method, static=static)
        self.outer_vertices = outer_vertices
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.center = center
        self.angle = angle

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        puzzle_radius = (
            self.puzzle_size // 2 - 1 if puzzle_size % 2 == 0 else self.puzzle_size // 2
        )
        puzzle_center = (puzzle_radius, puzzle_radius)
        self.points = Star.calculate_vertices(
            self.outer_vertices,
            self.outer_radius if self.outer_radius else puzzle_radius,
            self.inner_radius if self.inner_radius else puzzle_radius // 2,
            self.center if self.center else puzzle_center,
            self.angle,
        )
        self._draw_in_halves()

    @staticmethod
    def calculate_vertices(
        outer_vertices: int,
        outer_radius: int,
        inner_radius: int,
        center: tuple[int, int],
        angle: float,
    ):
        points = []
        cx, cy = center
        angle_step = 180.0 / outer_vertices
        angle = angle - 90  # rotated -90 so polygons are oriented North
        for _ in range(outer_vertices):
            # calculate outer point/vertex
            x, y = RegularPolygon.cos_sin_from_degrees(angle)
            points.append(
                (
                    int(round_half_up(x * outer_radius + cx)),
                    int(round_half_up(y * outer_radius + cy)),
                )
            )
            angle += angle_step
            # calculate inner point/vertex
            x, y = RegularPolygon.cos_sin_from_degrees(angle)
            points.append(
                (
                    int(round_half_up(x * inner_radius + cx)),
                    int(round_half_up(y * inner_radius + cy)),
                )
            )
            angle += angle_step
        return points