import os

from blender.level_exporter import LevelExporter

game_root = os.environ.get('A51_GAME_DATA', '/Users/ian/a51/pc/resources/app/game')
doom_root = os.environ.get('A51_DOOM_DATA', '/Users/ian/doom/a51mod')

maps_path = os.path.join(doom_root, 'maps')
textures_path = os.path.join(doom_root, 'textures')
materials_path = os.path.join(doom_root, 'materials')

os.makedirs(maps_path, exist_ok=True)
os.makedirs(textures_path, exist_ok=True)
os.makedirs(materials_path, exist_ok=True)

# write the hull material
hull_material = """textures/a51/hull
{
    {
        blend diffusemap
        map _black
    }
}"""
with open(os.path.join(materials_path, "hull.mtr"), "w") as myfile:
    myfile.write(hull_material)


LevelExporter(doom_root).export_level(game_root, 'DREAMLND')
#export_level(game_root, 'CAVES', './export/levels')
