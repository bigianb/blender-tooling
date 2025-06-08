import struct

class Ref:
    offset: int
    count: int
    pointing_at: int
    flags: int

class InevFile:
    """ Code to deal with reading an INEV file. """

    refs: list[type[Ref]]

    def __init__(self, data):
        self.data = data
        self.cursor_stack = []
        (self.sig,
        self.version,
        self.num_static_bytes,
        self.num_tables,
        self.num_dynamic_bytes) = struct.unpack_from("Iiiii", data)
        self.static_data_offset = 20
        self.cursor = self.static_data_offset

        if self.is_valid():
            self.dynamic_data_offset = self.static_data_offset + self.num_static_bytes
            self.resolve_table_offset = self.static_data_offset + self.num_static_bytes - self.num_tables * 16
            idx = self.resolve_table_offset
            self.refs = []
            for _ in range(self.num_tables):
                ref = Ref()
                (ref.offset, ref.count, ref.pointing_at, ref.flags) = struct.unpack_from("<iiiI", data, idx)
                idx += 16
                self.refs.append(ref)


    def resolve_pointer(self, expected_count):
        resolved_offset = -1
        source = self.cursor - self.static_data_offset
        for ref in self.refs:
            if ref.offset == source:
                if ref.flags == 3:
                    # points to static data
                    resolved_offset = ref.pointing_at + self.static_data_offset
                    if ref.count != expected_count:
                        print(f'Warning, expected count to be {expected_count}, but saw {ref.count}')
                elif ref.flags == 1:
                    # points to dynamic data
                    resolved_offset = ref.pointing_at + self.static_data_offset + self.num_static_bytes
                    if ref.count != expected_count:
                        print(f'Warning, expected count to be {expected_count}, but saw {ref.count}')
                else:
                    print('Flag not supported')
                break

        self.cursor += 4
        return resolved_offset

    def push_cursor(self, new_cursor):
        self.cursor_stack.append(self.cursor)
        self.cursor = new_cursor

    def pop_cursor(self):
        self.cursor = self.cursor_stack.pop()

    def is_valid(self):
        return self.sig == 0x56656e49
    
    def skip(self, num):
        """ skip num bytes. """
        self.cursor += num

    def align_16(self):
        self.cursor = ((self.cursor - self.static_data_offset + 0x0f) & ~0x0f) + self.static_data_offset

    def read_int(self):
        """ Reads a 32 bit integer """
        self.cursor += 4
        return struct.unpack_from('i', self.data, self.cursor - 4)[0]

    def read_u32(self):
        """ Reads an unsigned 32 bit integer """
        self.cursor += 4
        return struct.unpack_from('I', self.data, self.cursor - 4)[0]
    
    def read_i16(self):
        """ Reads a 16 bit integer. """
        self.cursor += 2
        return struct.unpack_from('h', self.data, self.cursor - 2)[0]
    
    def read_ui16(self):
        """ Reads an unsigned 16 bit integer. """
        self.cursor += 2
        return struct.unpack_from('H', self.data, self.cursor - 2)[0]
    
    def read_bounding_box(self):
        """ consists of 2 vectors min, max. """
       
        bb = struct.unpack_from('ffffffff', self.data, self.cursor)
        self.cursor += 4 * 4 * 2
        return bb

    def read_byte_array(self, count):
        """ Reads a byte array of given count. """
        start = self.cursor
        self.cursor += count
        return self.data[start:start+count] #struct.unpack_from(f'{count}B', self.data, start)

    def read_float_array(self, count):
        """ Reads an array of floats. """
        start = self.cursor
        self.cursor += 4 * count
        return struct.unpack_from(f'{count}f', self.data, start)
    
    def read_uint8_array(self, count):
        """ Reads an array of unsigned 8 bit integers. """
        start = self.cursor
        self.cursor += count
        return struct.unpack_from(f'{count}B', self.data, start)
    