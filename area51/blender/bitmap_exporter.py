
import os
from a51lib.dfs import Dfs
from a51lib.xbmp import XBmp


def export_bitmaps(resource_dfs: Dfs, output_path: str):
    """
    Export bitmaps from the given DFS to the specified output path.
    
    :param resource_dfs: DFS file containing resource data.
    :param output_path: Path to export the bitmaps.
    """

    os.makedirs(output_path, exist_ok=True)
    
    xbmp_files = resource_dfs.get_filenames('.xbmp')
    for xbmp_file in xbmp_files:
        xbmp_data = resource_dfs.get_file(xbmp_file)
        xbmp = XBmp()
        xbmp.read(xbmp_data)
        
        # Construct the output filename
        base_name = os.path.splitext(os.path.basename(xbmp_file))[0].casefold().strip()
        output_filename = os.path.join(output_path, f"{base_name}.png").replace('[', '_').replace(']', '_')
        
        # Write the bitmap to a PNG file
        xbmp.write_png(output_filename)
        