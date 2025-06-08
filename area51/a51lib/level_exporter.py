import bpy

from .dfs import Dfs
from .playsurface import Playsurface
from .rigid_geom import RigidGeom

def export_surfaces(col, zone, meshes, rigid_geoms, zone_no):
    surf_no = 0
    for surface in zone.surfaces:
        geom = rigid_geoms[surface.geom_name]

        if surface.geom_name in meshes:
            mesh = meshes[surface.geom_name]
        else:
            mesh = bpy.data.meshes.new(surface.geom_name)

            verts = []
            faces = []
            uvs = []

            v0_idx = 0
            for dlist in geom.dlists:
                for v in dlist.vertices:
                    pos = v.position
                    verts.append((pos[0], pos[1], pos[2]))
                for i in range(0, len(dlist.indices), 3):
                    vidx1 = dlist.indices[i]
                    vidx2 = dlist.indices[i+1]
                    vidx3 = dlist.indices[i+2]
                    faces.append((v0_idx+vidx1, v0_idx+vidx2, v0_idx+vidx3))
                    
                    vertex = dlist.vertices[vidx1]
                    uvs.append(vertex.uv[0])
                    uvs.append(vertex.uv[1])
                    vertex = dlist.vertices[vidx2]
                    uvs.append(vertex.uv[0])
                    uvs.append(vertex.uv[1])
                    vertex = dlist.vertices[vidx3]
                    uvs.append(vertex.uv[0])
                    uvs.append(vertex.uv[1])
                v0_idx += len(dlist.vertices)

            mesh.from_pydata(verts, [], faces)
            meshes[surface.geom_name] = mesh

            uv_data = mesh.uv_layers.new()
            uv_data.data.foreach_set('uv', uvs)


        obj = bpy.data.objects.new(
            'obj_z'+str(zone_no) + '_s'+str(surf_no), mesh)
        surf_no += 1
        obj.matrix_world = [surface.l2w[i:i+4] for i in range(0, 16, 4)]

        col.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

def export_level(game_root, level_name, export_dir, verbose=False):

    bpy.ops.wm.read_factory_settings()

    level_dfs = Dfs()
    level_dfs.open(game_root+'/LEVELS/CAMPAIGN/'+level_name+'/LEVEL')
    if verbose:
        print('\n\nLEVEL.DFS contents:\n')
        level_dfs.list_files()

        loadscript = level_dfs.get_file('LOADSCRIPT.TXT')
        print(loadscript.decode('utf-8'))

    playsurface = Playsurface()
    playsurface.init(level_dfs.get_file('LEVEL_DATA.PLAYSURFACE'))
    if verbose:
        print('\n\nPlaysurface:\n')
        playsurface.describe()

    resource_dfs = Dfs()
    resource_dfs.open(game_root+'/LEVELS/CAMPAIGN/'+level_name+'/RESOURCE')
    if verbose:
        print('\n\nRESOURCE.DFS contents:\n')
        resource_dfs.list_files()

    rigid_geoms = {}
    for gname in playsurface.geoms:
        geom_data = resource_dfs.get_file(gname)
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
    V3Dareas = (a for s in screens for a in s.areas if a.type == 'VIEW_3D')
    V3Dspaces = (s for a in V3Dareas for s in a.spaces if s.type == 'VIEW_3D')
    for space in V3Dspaces:
        space.clip_start = 10
        space.clip_end = 150000

    meshes = {}
    zone_no = 0
    for zone in playsurface.zones:
        col = bpy.data.collections.new("Zone "+str(zone_no))
        bpy.context.scene.collection.children.link(col)
        export_surfaces(col, zone, meshes, rigid_geoms, zone_no)
        zone_no += 1
    for zone in playsurface.portals:
        col = bpy.data.collections.new("Portal "+str(zone_no))
        bpy.context.scene.collection.children.link(col)
        export_surfaces(col, zone, meshes, rigid_geoms, zone_no)
        zone_no += 1

    # remove mesh Cube
    if "Cube" in bpy.data.meshes:
        mesh = bpy.data.meshes["Cube"]
        print("removing mesh", mesh)
        bpy.data.meshes.remove(mesh)

    bpy.ops.wm.save_as_mainfile(
        filepath=export_dir+'/'+level_name+'.blend', check_existing=False)
