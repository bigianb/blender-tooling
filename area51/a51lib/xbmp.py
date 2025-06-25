
from enum import IntEnum
import png

from .data_reader import DataReader

class XBmpFormat(IntEnum):
    FMT_3ARGB_8888 = 3

class XBmp:
     
   orig_pixel_data: bytes
   clut_data: bytes

   width: int
   height: int
   physical_width: int

   def read(self, bin_data):
      reader = DataReader(bin_data)
      self.data_size = reader.read_int()
      self.clut_size = reader.read_int()
      self.width = reader.read_int()
      self.height = reader.read_int()
      self.physical_width = reader.read_int()
      self.flags = reader.read_u32()
      self.num_mips = reader.read_int()
      self.format = reader.read_int()
      self.orig_pixel_data = reader.read_byte_array(self.data_size)
      if self.clut_size > 0:
         self.clut_data = reader.read_byte_array(self.clut_size)
      else:
         self.clut_data = None
      
   

   def write_png(self, filename):
      converted_pixel_data = self._convert_to_32bpp()
      argb_data = []
      for row in range (0, self.height):
         row_pix = []
         argb_data.append(row_pix)
         pix_idx = row * self.physical_width * 4
         for _ in range (0, self.width):
            row_pix.append(converted_pixel_data[pix_idx + 1])
            row_pix.append(converted_pixel_data[pix_idx + 2])
            row_pix.append(converted_pixel_data[pix_idx + 3])
            row_pix.append(converted_pixel_data[pix_idx])
            pix_idx += 4
      png_obj = png.from_array(argb_data, mode='RGBA')
      with open(filename, 'wb') as file:
         png_obj.write(file)


# pypng docs https://drj11.gitlab.io/pypng/
   def _convert_to_32bpp(self):
      if self.format == XBmpFormat.FMT_3ARGB_8888:
         return self.orig_pixel_data
      print("*** Unimplemented format: " + str(format))
      

     