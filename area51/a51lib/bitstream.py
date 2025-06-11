import struct

class Bitstream:
    def __init__(self, data, bitpos=0):
        self.data = data
        self.bitpos = bitpos
            
    def _read_raw(self, num_bits) -> int:
        left_offset=self.bitpos & 7
        byte_pos = self.bitpos >> 3
        self.bitpos += num_bits

        num_bytes = (num_bits + 7) >> 3
        if left_offset > 0:
            num_bytes += 1

        mask = 0xFF >> left_offset
        unshifted = struct.unpack_from(f'{num_bytes}B', self.data, byte_pos)
        shifted = unshifted[0] & mask
        for i in range(1, num_bytes-1):
            shifted <<= 8
            shifted |= unshifted[i]
        # we now have left_offset bits that we need to get from unshifted[4]
        if left_offset > 0:
            shifted <<= left_offset
            shifted |= (unshifted[num_bytes-1] >> (8 - left_offset))
        return shifted

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