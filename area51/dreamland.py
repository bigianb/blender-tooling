import os

from a51lib.level_exporter import export_level

game_root = os.environ.get('A51_GAME_DATA', '/Users/ian/a51/pc/resources/app/game')

os.makedirs('./export/levels', exist_ok=True)

export_level(game_root, 'DREAMLND', './export/levels', verbose=False)
#export_level(game_root, 'CAVES', './export/levels')
