import os

from a51lib.dfs import Dfs
from a51lib.playsurface import Playsurface
from a51lib.rigid_geom import RigidGeom

game_root = os.environ.get('A51_GAME_DATA', '/Users/ian/a51/pc/resources/app/game')

dreamland_dfs = Dfs()
dreamland_dfs.open(game_root+'/LEVELS/CAMPAIGN/DREAMLND/LEVEL')

print('\n\nLEVEL.DFS contents:\n')
dreamland_dfs.list_files()

#loadscript = dreamland_dfs.get_file('LOADSCRIPT.TXT')
#print(loadscript.decode('utf-8'))

playsurface = Playsurface()
playsurface.init(dreamland_dfs.get_file('LEVEL_DATA.PLAYSURFACE'))
print('\n\nPlaysurface:\n')
playsurface.describe()

dreamland_resource_dfs = Dfs()
dreamland_resource_dfs.open(game_root+'/LEVELS/CAMPAIGN/DREAMLND/RESOURCE')
print('\n\nRESOURCE.DFS contents:\n')
dreamland_resource_dfs.list_files()

for gname in playsurface.geoms:
    geom_data = dreamland_resource_dfs.get_file(gname)
    if geom_data == None:
        print(f'Failed to find data for {gname}')
        continue
    geom = RigidGeom()
    geom.read(geom_data)
    if geom.is_valid():
        print(f'\nread {gname}')
        geom.describe()
    else:
        print(f'Failed to read {gname}')
