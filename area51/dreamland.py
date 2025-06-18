import os

from a51lib.level_exporter import export_level

game_root = os.environ.get('A51_GAME_DATA', '/Users/ian/a51/pc/resources/app/game')

os.makedirs('./export/levels', exist_ok=True)

dreamland_caulk = [
    # min_x, min_y, min_z, max_x, max_y, max_z
    [-1930, 0, -1535, -1470, 400, -1535]
]

export_level(game_root, 'DREAMLND', './export/levels', dreamland_caulk, verbose=False)
#export_level(game_root, 'CAVES', './export/levels')
