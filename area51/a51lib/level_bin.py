from .data_reader import DataReader
from .bitstream import Bitstream

class LevelObject:
    type_index: int
    num_properties: int
    start_property_idx: int
    guid: int

class LevelBin:

    objects: list[LevelObject]

    def init(self, bin_data):
        """ Initialise the object by decoding the serialised bin_data. """
        reader = DataReader(bin_data)
        self.version = reader.read_u16()
        reader.skip(4)
        self.num_objects = reader.read_int()
        self.num_properties = reader.read_int()
        bitstream_len = reader.read_int()
        

        for i in range(0, self.num_objects):
            obj = LevelObject()

            self.objects.append(obj)

        bitstream = Bitstream(bin_data, reader.cursor * 8)
