from .data_reader import DataReader
from .bitstream import Bitstream
from enum import IntEnum


class LevelObject:
    type_index: int
    num_properties: int
    start_property_idx: int
    guid: int
    # read from the dictionary via the type_index
    type_name: str
    properties: dict


class LevelProperty:
    type_index: int
    name_index: int
    name: str

class PropertyType(IntEnum):
    NULL = 0
    FLOAT = 1
    INT = 2
    BOOL = 3
    VECTOR2 = 4
    VECTOR3 = 5
    ROTATION = 6
    ANGLE = 7
    BBOX = 8
    GUID = 9
    COLOR = 10
    STRING = 11
    ENUM = 12
    BUTTON = 13
    EXTERNAL = 14
    FILENAME = 15

class LevelBin:

    objects: list[LevelObject]
    properties: list[LevelProperty]
    dictionary: list[str]

    def init(self, bin_data, dict_data):
        """ Initialise the object by decoding the serialised bin_data. """
        self._init_dictionary(dict_data)
        reader = DataReader(bin_data)
        self.version = reader.read_u16()
        reader.skip(4)
        self.num_objects = reader.read_int()
        self.num_properties = reader.read_int()
        reader.read_int()   # bitstream length. We don't need it.

        self._read_objects(reader)
        self._read_properties(reader)

        bitstream = Bitstream(bin_data, reader.cursor * 8)
        self._init_objects_from_bitstream(bitstream)

    def _init_dictionary(self, dict_data):
        self.dictionary = []
        reader = DataReader(dict_data)
        while reader.has_data():
            self.dictionary.append(reader.read_string())

    def _init_objects_from_bitstream(self, bitstream: Bitstream):
        object_type_names = set()
        for obj in self.objects:
            object_type_names.add(obj.type_name)
            obj.properties = {}
            start_idx = obj.start_property_idx
            end_idx = start_idx + obj.num_properties

            for prop_idx in range(start_idx, end_idx):
                prop = self.properties[prop_idx]
                self._add_prop(obj.properties, prop, bitstream)
        print("Found the following object types\n" + str(object_type_names))

    def _add_prop(self, properties: dict, prop: LevelProperty, bitstream: Bitstream):
        clean_type = prop.type_index & 0xFF
        pval =0
        match clean_type:
            case PropertyType.FLOAT:
                pval = bitstream.read_float()
                properties[prop.name] = pval
            case PropertyType.INT:
                pval = bitstream.read_s32()
            case PropertyType.BOOL:
                pval = bitstream.read_bool()
            case PropertyType.VECTOR2:
                pval = bitstream.read_v2()
            case PropertyType.VECTOR3:
                pval = bitstream.read_v3()
            case PropertyType.ROTATION:
                pval = bitstream.read_v3() # pitch, roll, yaw
            case PropertyType.ANGLE:
                pval = bitstream.read_float()
            case PropertyType.BBOX:
                pval = bitstream.read_bounding_box()
            case PropertyType.GUID:
                pval =bitstream.read_u64()
            case PropertyType.COLOR:
                pval = bitstream.read_colour()
            case PropertyType.STRING:
                pval = bitstream.read_string()
            case PropertyType.ENUM:
                pval = bitstream.read_string()
            case PropertyType.BUTTON:
                pval = bitstream.read_string()
            case PropertyType.EXTERNAL:
                pval = bitstream.read_string()
            case PropertyType.FILENAME:
                pval = bitstream.read_string()

            case _:
                raise RuntimeError("Uknown property type: " + str(clean_type))
            
        print(prop.name + ' = ' + str(pval))


    def _read_objects(self, reader: DataReader):
        self.objects = []
        for _ in range(0, self.num_objects):
            obj = LevelObject()
            obj.type_index = reader.read_i16()
            obj.type_name = self.dictionary[obj.type_index]
            obj.num_properties = reader.read_i16()
            obj.start_property_idx = reader.read_int()
            obj.guid = reader.read_u64()
            self.objects.append(obj)

    def _read_properties(self, reader: DataReader):
        self.properties = []
        for _ in range(0, self.num_properties):
            prop = LevelProperty()
            prop.type_index = reader.read_u16()
            prop.name_index = reader.read_u16()
            prop.name = self.dictionary[prop.name_index]
            self.properties.append(prop)
