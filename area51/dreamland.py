from a51lib.dfs import Dfs
from a51lib.playsurface import Playsurface

game_root = '/Users/ian/a51/pc/resources/app/game'

dreamland_dfs = Dfs()
dreamland_dfs.open(game_root+'/LEVELS/CAMPAIGN/DREAMLND/LEVEL')
dreamland_dfs.list_files()

#loadscript = dreamland_dfs.get_file('LOADSCRIPT.TXT')
#print(loadscript.decode('utf-8'))

playsurface = Playsurface()
playsurface.init(dreamland_dfs.get_file('LEVEL_DATA.PLAYSURFACE'))

