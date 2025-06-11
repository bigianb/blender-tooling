import struct

class Bitstream:
    def __init__(self, data, bitpos=0):
        self.data = data
        self.bitpos = bitpos
            
    def _read_raw(self, num_bits) -> int:
        leftOffset = self.bitpos & 7
        rightOffset = (40 - leftOffset - num_bits)
    
        byte_pos = self.bitpos >> 3
        end_pos = ((self.bitpos + num_bits - 1) >> 3) + 1

        self.bitpos += num_bits
        readMask = (0xFFFFFFFFFF >> leftOffset) & (0xFFFFFFFFFF << rightOffset)
        dataMask = 0

        shift = 32
        while byte_pos != end_pos:
            b = struct.unpack_from('B', self.data, byte_pos)[0]
            byte_pos += 1
            dataMask |= (b << shift)
            shift -= 8

        return (dataMask & readMask) >> rightOffset


    def read_float(self) -> float:
        raw = self._read_raw(32)
        buf = struct.pack('I', raw)
        return struct.unpack('f', buf)[0]
    
    def read_s32(self) -> int:
        self.bitpos += 32
        return 0
    
    def read_u64(self) -> int:
        self.bitpos += 64
        return 0
    
    def read_bool(self) -> int:
        return self._read_raw(1) == 1
        
    def read_v2(self) -> list[float]:
        return [self.read_float(), self.read_float()]
    
    def read_v3(self) -> list[float]:
         return [self.read_float(), self.read_float(), self.read_float()]

    def read_bounding_box(self) -> list[float]:
        self.bitpos += 6 * 32
        return [0, 0, 0, 0, 0, 0]
    
    def read_colour(self) -> int:
        self.bitpos += 32
        return 0
    
    def read_string(self) -> str:
        len = self._read_raw(8)
        s = ''
        # This is wrong. The way the buffer has to be read is complex and bizarre.
        # a sequence 0x5c 0x52 starting at bit offset 6 will return 0x48 and not 0x14
        # as you may expect.
        while len > 0:
            c = self._read_raw(8)
            if c != 0:
                # len includes the null terminator
                s += chr(c)
            len -= 1
        
        return s