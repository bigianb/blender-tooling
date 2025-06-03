import struct

def read_z_string(data, offset):
    output = ''
    while data[offset] != 0:
        output += chr(data[offset])
        offset += 1
    return output


class Surface:
    geom_name = ''

class Playsurface:
    
    version = -1
    num_zones = 0
    num_portals = 0
    num_geoms = 0
    geoms = []
    zones = []
    portals = []

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
            self.zones.append(zone)

        self.portals = []
        for _ in range(self.num_portals):
            (index, portal) = self.read_zone_info(bin_data, index)
            self.portals.append(portal)

    def read_zone_info(self, bin_data, offset):
        zone = {}
       # file_offset = struct.unpack_from('I', bin_data, offset+4)[0]
       # num_surfaces = struct.unpack_from('I', bin_data, offset+8)[0]
       # num_colours = struct.unpack_from('I', bin_data, offset+16)[0]
        offset += 28

        # todo read surfaces

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
        
