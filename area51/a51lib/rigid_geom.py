from .inev_file import InevFile
from .geom import Geom

class RigidVertex:
    position: list[float]
    normal: list[float]
    colour: list[int]
    uv: list[float]

    def __init__(self):
        self.position = [0.0, 0.0, 0.0]
        self.normal = [0.0, 0.0, 0.0]
        self.colour = [255, 255, 255, 255]
        self.uv = [0.0, 0.0]

class RigidDlist:
    indices: list[int]
    vertices: list[RigidVertex]
    bone_index: int

    def __init__(self):
        self.indices = []
        self.vertices = []
        self.bone_index = -1

class RigidGeom:

    # use composition rather than inheritance
    geom: Geom
    valid: bool
    dlists: list[RigidDlist]

    def __init__(self):
        self.geom = None
        self.valid = False
        self.dlists = []
        self.num_dlist = 0

    def is_valid(self):
        return self.valid and self.geom != None and self.geom.is_valid()

    def read(self, bin_data):
        inev_file = InevFile(bin_data)
        self.valid = inev_file.is_valid()
        if not self.valid:
            return
        self.read_inev(inev_file)

    def read_inev(self, inev_file: InevFile):
        self.geom = Geom()
        self.geom.read_inev(inev_file)
        inev_file.skip(4)

        # collision data - skip for now
        inev_file.skip(32)      # bbox
        inev_file.skip(4*4 + 4*2 + 3*4)
        inev_file.align_16()
        self.num_dlist = inev_file.read_int()

        if self.geom.platform != 1:
            print("Only PC platform is supported currently")
            self.valid = False
            return
        dlist_array_cursor = inev_file.resolve_pointer(self.num_dlist)
        inev_file.push_cursor(dlist_array_cursor)
        self._read_dlist_pc(inev_file)
        inev_file.pop_cursor()
        
    def _read_dlist_pc(self, inev_file: InevFile):
        for _ in range(self.num_dlist):
            dl = RigidDlist()
            num_indices = inev_file.read_u32()
            indices_cursor = inev_file.resolve_pointer(num_indices)
            inev_file.push_cursor(indices_cursor)
            for _ in range(num_indices):
                dl.indices.append(inev_file.read_u16())
            inev_file.pop_cursor()

            num_vertices = inev_file.read_int()
            vertices_cursor = inev_file.resolve_pointer(num_vertices)
            inev_file.push_cursor(vertices_cursor)
            for _ in range(num_vertices):
                vertex = RigidVertex()
                vertex.position = inev_file.read_float_array(3)
                vertex.normal = inev_file.read_float_array(3)
                vertex.colour = inev_file.read_uint8_array(4)
                vertex.uv = inev_file.read_float_array(2)
                dl.vertices.append(vertex)
            inev_file.pop_cursor()

            dl.bone_index = inev_file.read_int()
            inev_file.skip(4)
            self.dlists.append(dl)

    def describe(self):
        if not self.is_valid():
            print("RigidGeom is not valid")
            return
        self.geom.describe()

