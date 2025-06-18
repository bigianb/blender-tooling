import os

from a51lib.level_exporter import export_level

game_root = os.environ.get('A51_GAME_DATA', '/Users/ian/a51/pc/resources/app/game')
doom_root = os.environ.get('A51_DOOM_DATA', '/Users/ian/doom/RBDOOM-3-BFG/base')

sub_path = 'a51'
maps_path = os.path.join(doom_root, 'maps', sub_path)
textures_path = os.path.join(doom_root, 'textures', sub_path)

os.makedirs(maps_path, exist_ok=True)

dreamland_caulk = [
    # min_x, min_y, min_z, max_x, max_y, max_z
    [-1930, 0, -1535, -1470, 400, -1535],
    [-10100.0, -3399.0, -13367.0, -6100, -3399.0, -17022],
    [-500.0, 200.0, -11950.0, 910, 200.0, -9279],
]
# min x = -500
# max x =  910
# min z = -11950
# max z = -9279
# y = 200

export_level(game_root, 'DREAMLND', doom_root, sub_path, dreamland_caulk, verbose=False)
#export_level(game_root, 'CAVES', './export/levels')
