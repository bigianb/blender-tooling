import struct

class Playsurface:
    
    def init(self, bin_data):
        ints = struct.unpack_from('IIII', bin_data)
        self.version = ints[0]
        self.num_zones = ints[1]
        self.num_portals = ints[2]
        self.num_geoms = ints[3]
        pass

    def describe(self):
        print(f'Version:     {self.version}')
        print(f'NumZones:    {self.num_zones}')
        print(f'Num Portals: {self.num_portals}')
        print(f'Num Geoms:   {self.num_geoms}')
