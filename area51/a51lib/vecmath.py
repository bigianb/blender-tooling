
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
            raise ValueError(f"Invalid number of floats for BoundingBox: {len(floats)}. Expected 6 or 8.")


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
    

    def __repr__(self):
        return f"BoundingBox({self.min_x}, {self.min_y}, {self.min_z}, {self.max_x}, {self.max_y}, {self.max_z})"