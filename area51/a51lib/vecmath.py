import numpy as np

class Matrix4x4:

    m4: np.ndarray

    def __init__(self):
        self.m4 = np.eye(4)

    def scale(self, val):
        scaling_matrix = np.array([[val, 0, 0, 0],
                                  [0, val, 0, 0],
                                  [0, 0, val, 0],
                                  [0, 0, 0, 1]], dtype=float)

        self.m4 = scaling_matrix @ self.m4

    def translate(self, trans):
        translation_matrix = np.array([[1.0, 0, 0, trans[0]],
                                       [0, 1.0, 0, trans[1]],
                                       [0, 0, 1.0, trans[2]],
                                       [0, 0, 0, 1]], dtype=float)
        self.m4 = translation_matrix @ self.m4

    def convert_zup_to_yup(self):
        """ Convert from being z-up to y-up. Basically a 90 degree roation around the x-axis.
            Special case to keep numbers accurate.
        """
        cos_a = 0
        sin_a = 1
        rotation_matrix = np.array([[1, 0, 0, 0],
                                    [0, cos_a, -sin_a, 0],
                                    [0, sin_a, cos_a, 0],
                                    [0, 0, 0, 1]], dtype=float)
        self.m4 = rotation_matrix @ self.m4

    def transform(self, x: float, y: float, z: float) -> list[float]:
        x1, y1, z1, _ = self.m4 @ [x, y, z, 1]
        return (x1, y1, z1)


class BoundingBox:

    def __init__(self, floats: list[float] = None):

        if floats is None:
            self.min_x = self.min_y = self.min_z = 0.0
            self.max_x = self.max_y = self.max_z = 0.0
            return

        if len(floats) == 8:
            # x, y, z, w
            self.min_x, self.min_y, self.min_z, _, self.max_x, self.max_y, self.max_z, _ = floats
        elif len(floats) == 6:
            self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z = floats
        else:
            raise ValueError(
                f"Invalid number of floats for BoundingBox: {len(floats)}. Expected 6 or 8.")

    def contains(self, x, y, z):
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y and self.min_z <= z <= self.max_z

    def add(self, other: 'BoundingBox') -> 'BoundingBox':
        if not isinstance(other, BoundingBox):
            raise TypeError("Can only add another BoundingBox.")
        return BoundingBox((
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            min(self.min_z, other.min_z),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y),
            max(self.max_z, other.max_z))
        )

    def centre(self):
        return (
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2
        )

    def size(self):
        return (
            self.max_x - self.min_x,
            self.max_y - self.min_y,
            self.max_z - self.min_z
        )

    def transform(self, mtx: Matrix4x4) -> 'BoundingBox':
        x0, y0, z0 = mtx.transform(self.min_x, self.min_y, self.min_z)
        x1, y1, z1 = mtx.transform(self.max_x, self.max_y, self.max_z)

        return BoundingBox([min(x0, x1), min(y0, y1), min(z0, z1), max(x0, x1), max(y0, y1), max(z0, z1)])

    def __repr__(self):
        return f"BoundingBox({self.min_x}, {self.min_y}, {self.min_z}, {self.max_x}, {self.max_y}, {self.max_z})"


