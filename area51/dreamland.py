import os
import bpy

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

rigid_geoms = {}
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
        rigid_geoms[gname] = geom
    else:
        print(f'Failed to read {gname}')

bpy.context.scene.unit_settings.system = 'NONE'
screens = (s for w in bpy.data.workspaces for s in w.screens)
V3Dareas = (a for s in screens for a in s.areas if a.type=='VIEW_3D')
V3Dspaces = (s for a in V3Dareas for s in a.spaces if s.type=='VIEW_3D')
for space in V3Dspaces:
    space.clip_start = 1
    space.clip_end = 100000

zone1 = playsurface.zones[0]
col = bpy.data.collections.new("Zone1")
bpy.context.scene.collection.children.link(col)
# Create a mesh for each surface in zone1 and link it to the collection
meshes = {}
surf_no = 0
for surface in zone1.surfaces:
    geom = rigid_geoms[surface.geom_name]

    if surface.geom_name in meshes:
        mesh = meshes[surface.geom_name]
    else:
        mesh = bpy.data.meshes.new(surface.geom_name)

        verts = []
        faces = []

        v0_idx = 0
        for dlist in geom.dlists:
            for v in dlist.vertices:
                pos = v.position
                verts.append((pos[0], pos[1], pos[2]))
            for i in range(0, len(dlist.indices), 3):
                faces.append((v0_idx+dlist.indices[i], v0_idx+dlist.indices[i+1], v0_idx+dlist.indices[i+2]))
            v0_idx += len(dlist.vertices)

        mesh.from_pydata(verts, [], faces)    
        meshes[surface.geom_name] = mesh

    obj = bpy.data.objects.new('obj'+str(surf_no), mesh)
    surf_no += 1
    obj.matrix_world = [surface.l2w[i:i+4] for i in range(0, 16, 4)]

    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj


# remove mesh Cube
if "Cube" in bpy.data.meshes:
    mesh = bpy.data.meshes["Cube"]
    print("removing mesh", mesh)
    bpy.data.meshes.remove(mesh)

bpy.ops.wm.save_as_mainfile(filepath='dreamland.blend', check_existing=False)
