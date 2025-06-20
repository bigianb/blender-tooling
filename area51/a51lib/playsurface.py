import struct

from .vecmath import BoundingBox

def read_z_string(data, offset):
    output = ''
    while data[offset] != 0:
        output += chr(data[offset])
        offset += 1
    return output

class Surface:
    def __init__(self):
        self.l2w = [0.0] * 16  # 4x4 matrix
        self.bounding_box = BoundingBox()
        self.attr_bits = 0
        self.colour_index = 0
        self.geom_name = ''
        self.render_flags = 0
        self.zone_1 = 0
        self.zone_2 = 0

class ZoneInfo:
    surfaces: list[Surface]
    def __init__(self):
        self.surfaces = []
        self.colours = []

class Playsurface:
    
    version: int
    num_zones: int
    num_portals: int
    num_geoms: int
    geoms: list[str]
    zones: list[ZoneInfo]
    portals: list[ZoneInfo]

    def init(self, bin_data):
        ints = struct.unpack_from('IIII', bin_data)
        self.version = ints[0]
        self.num_zones = ints[1]
        self.num_portals = ints[2]
        self.num_geoms = ints[3]
        
        index = self.readSpatialDB(bin_data, 16)
        self.geoms = []
        for _ in range(self.num_geoms):
            self.geoms.append(read_z_string(bin_data, index))
            index += 128

        self.zones = []
        for _ in range(self.num_zones):
            (index, zone) = self.read_zone_info(bin_data, index)
            if len(zone.surfaces) > 0:
                self.zones.append(zone)

        self.portals = []
        for _ in range(self.num_portals):
            (index, portal) = self.read_zone_info(bin_data, index)
            if len(portal.surfaces) > 0:
                self.portals.append(portal)

    def read_zone_info(self, bin_data, offset):
        zone = ZoneInfo()
        file_offset = struct.unpack_from('I', bin_data, offset+4)[0]
        num_surfaces = struct.unpack_from('I', bin_data, offset+8)[0]
        num_colours = struct.unpack_from('I', bin_data, offset+16)[0]
        offset += 28

        zone_info_offset = file_offset
        for _ in range(num_surfaces):
            surface = Surface()
            surface.l2w = struct.unpack_from('16f', bin_data, zone_info_offset)
            zone_info_offset += 64  # 4x4 matrix is 16 floats, each float is 4 bytes)
            surface.bounding_box = BoundingBox(struct.unpack_from('8f', bin_data, zone_info_offset))
            zone_info_offset += 32
            surface.attr_bits = struct.unpack_from('I', bin_data, zone_info_offset)[0]
            zone_info_offset += 4
            surface.colour_index = struct.unpack_from('I', bin_data, zone_info_offset)[0]
            zone_info_offset += 4
            zone_info_offset += 4*4
            surface.zone_1 = struct.unpack_from('B', bin_data, zone_info_offset)[0]
            surface.zone_2 = struct.unpack_from('B', bin_data, zone_info_offset + 1)[0]
            geom_indx = struct.unpack_from('H', bin_data, zone_info_offset + 2)[0]
            surface.geom_name = self.geoms[geom_indx] if geom_indx < len(self.geoms) else ''
            zone_info_offset += 4
            surface.render_flags = struct.unpack_from('I', bin_data, zone_info_offset)[0]
            zone_info_offset += 4
            zone.surfaces.append(surface)

        return offset, zone

    def readSpatialDB(self, bin_data, offset):
        # cell_size = struct.unpack_from('I', bin_data, offset)[0]
        num_cells = struct.unpack_from('I', bin_data, offset+4)[0]
        # num_surfaces = struct.unpack_from('I', bin_data, offset+8)[0]
        offset += 12
        offset += 8 * 1021  # Skip hash table
        offset += num_cells * 24    # Skip cell data
        return offset

    def describe(self):
        print(f'Version:     {self.version}')
        print(f'NumZones:    {self.num_zones}')
        print(f'Num Portals: {self.num_portals}')
        print(f'Num Geoms:   {self.num_geoms}')
        
