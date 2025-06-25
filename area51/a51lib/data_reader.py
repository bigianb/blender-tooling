import struct

class DataReader:
    """ Code to deal with reading binary data. """

    cursor: int
    data: bytes
    len: int

    def __init__(self, data: bytes, cursor: int = 0):
        self.data = data
        self.len = len(data)
        self.cursor_stack = []
        self.cursor = cursor

    def push_cursor(self, new_cursor):
        self.cursor_stack.append(self.cursor)
        self.cursor = new_cursor

    def pop_cursor(self):
        self.cursor = self.cursor_stack.pop()
    
    def has_data(self)-> bool:
        return self.cursor < self.len

    def skip(self, num):
        """ skip num bytes. """
        self.cursor += num

    def align_16(self):
        self.cursor = ((self.cursor + 0x0f) & ~0x0f)

    def read_int(self):
        """ Reads a 32 bit integer """
        self.cursor += 4
        return struct.unpack_from('i', self.data, self.cursor - 4)[0]

    def read_u32(self):
        """ Reads an unsigned 32 bit integer """
        self.cursor += 4
        return struct.unpack_from('I', self.data, self.cursor - 4)[0]
    
    def read_u64(self):
        """ Reads an unsigned 64 bit integer """
        self.cursor += 8
        return struct.unpack_from('Q', self.data, self.cursor - 8)[0]
    
    def read_i16(self):
        """ Reads a 16 bit integer. """
        self.cursor += 2
        return struct.unpack_from('h', self.data, self.cursor - 2)[0]
    
    def read_u16(self):
        """ Reads an unsigned 16 bit integer. """
        self.cursor += 2
        return struct.unpack_from('H', self.data, self.cursor - 2)[0]
    
    def read_byte(self):
        """ Reads an unsigned 8 bit integer. """
        self.cursor += 1
        return struct.unpack_from('B', self.data, self.cursor - 1)[0]

    def read_float(self) -> float:
        """ Reads a float. """
        self.cursor += 4
        return struct.unpack_from('f', self.data, self.cursor - 4)[0]
    
    def read_bounding_box(self):
        """ consists of 2 vectors min, max. """
       
        bb = struct.unpack_from('ffffffff', self.data, self.cursor)
        self.cursor += 4 * 4 * 2
        return bb

    def read_byte_array(self, count: int) -> bytes:
        """ Reads a byte array of given count. """
        start = self.cursor
        self.cursor += count
        return self.data[start:start+count]

    def read_float_array(self, count: int) -> list[float]:
        """ Reads an array of floats. """
        start = self.cursor
        self.cursor += 4 * count
        return struct.unpack_from(f'{count}f', self.data, start)
    
    def read_uint8_array(self, count: int):
        """ Reads an array of unsigned 8 bit integers. """
        start = self.cursor
        self.cursor += count
        return struct.unpack_from(f'{count}B', self.data, start)
    
    def read_string(self) -> str:
        output = ''
        while self.has_data() and self.data[self.cursor] != 0:
            output += chr(self.data[self.cursor])
            self.cursor += 1
        # step over null terminator
        self.cursor += 1
        return output
    