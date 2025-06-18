import bpy
import os

from .blender_utils import remove_mesh, set_clips

from .info_reader import InfoReader

from .dfs import Dfs
from .playsurface import Playsurface
from .rigid_geom import RigidGeom
from .level_bin import LevelBin

def dlist_to_verts_faces(dlist):
    verts = []
    faces = []
    uvs = []
    
    for v in dlist.vertices:
        pos = v.position
        verts.append((pos[0], pos[1], pos[2]))
    for i in range(0, len(dlist.indices), 3):
        vidx1 = dlist.indices[i]
        vidx2 = dlist.indices[i+1]
        vidx3 = dlist.indices[i+2]
        faces.append((vidx1, vidx2, vidx3))
        
        vertex = dlist.vertices[vidx1]
        uvs.append(vertex.uv[0])
        uvs.append(vertex.uv[1])
        vertex = dlist.vertices[vidx2]
        uvs.append(vertex.uv[0])
        uvs.append(vertex.uv[1])
        vertex = dlist.vertices[vidx3]
        uvs.append(vertex.uv[0])
        uvs.append(vertex.uv[1])
    return verts, faces, uvs

def export_surface(surface, name_prefix, col, meshes, materials, rigid_geoms: list[RigidGeom], tex_dir):
    geom = rigid_geoms[surface.geom_name]
    mesh_no = 0
    for geom_mesh in geom.geom.meshes:
        for submesh_idx in range (geom_mesh.idx_sub_mesh, geom_mesh.idx_sub_mesh + geom_mesh.num_sub_meshes):
            submesh = geom.geom.sub_meshes[submesh_idx]
            key = surface.geom_name + '_' + geom_mesh.name + '_' + str(submesh_idx)
            if key in meshes:
                mesh = meshes[key]
            else:
                mesh = bpy.data.meshes.new(key)
                
                dlist = geom.dlists[submesh.idx_dlist]
                verts, faces, uvs = dlist_to_verts_faces(dlist)    

                mesh.from_pydata(verts, [], faces)
                meshes[key] = mesh

                uv_data = mesh.uv_layers.new()
                uv_data.data.foreach_set('uv', uvs)
                    
            obj = bpy.data.objects.new(name_prefix + '_' + str(mesh_no) + '_' + str(submesh_idx), mesh)
        
            texture_idx = geom.geom.materials[submesh.idx_material].texture_index
            texture = geom.geom.textures[texture_idx]
            if texture.filename in materials:
                material = materials[texture.filename]
            else:
                # https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material
                tex_basename = texture.filename.split('.')[0].upper()
                img_path = os.path.join(tex_dir, tex_basename+".png")
                img_path = os.path.abspath(img_path)

                try:
                    im = bpy.data.images.load(img_path, check_existing=True)
                    im.name = tex_basename+".png"
                except RuntimeError:
                    im = bpy.data.images.new(tex_basename+".png", 128, 128)
                    # allow the path to be resolved later
                    im.filepath = img_path
                    im.source = 'FILE'

                material = bpy.data.materials.new('Material_'+texture.filename)
                material.use_nodes = True
                teximage_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                teximage_node.image = im
                bsdf_node = material.node_tree.nodes["Principled BSDF"]
                material.node_tree.links.new(bsdf_node.inputs["Base Color"], teximage_node.outputs["Color"])

                materials[texture.filename] = material
            obj.active_material = material
            obj.matrix_world = [surface.l2w[i:i+4] for i in range(0, 16, 4)]

            col.objects.link(obj)

        mesh_no += 1

def export_surfaces(col, zone, meshes, materials, rigid_geoms: list[RigidGeom], zone_no, tex_dir):
    surf_no = 0
    for surface in zone.surfaces:
        export_surface(surface, 'obj_z'+str(zone_no) + '_s'+str(surf_no), col, meshes, materials, rigid_geoms, tex_dir)
        surf_no += 1

def collect_rigid_geoms(geom_names: list[str], dfs: Dfs, verbose: bool):
    rigid_geoms = {}
    for gname in geom_names:
        geom_data = dfs.get_file(gname)
        if geom_data == None:
            print(f'Failed to find data for {gname}')
            continue
        geom = RigidGeom()
        geom.read(geom_data)
        if geom.is_valid():
            if verbose:
                print(f'\nread {gname}')
                geom.describe()
            rigid_geoms[gname] = geom
        else:
            print(f'Failed to read {gname}')
    return rigid_geoms

def loadInfo(info_data):
    lines = info_data.decode('utf-8').splitlines()
    reader = InfoReader(lines)
    while header := reader.read_header():
        if header.type == 'PlayerInfo':
            # Position, Pitch, Yaw
            pos = header.fields[0]['Position']
            pitch = header.fields[0]['Pitch']
            yaw = header.fields[0]['Yaw']

        elif header.type == 'Info':
            pass
        else:
            print(f"Unknown header type: {header.type}")
    return pos, pitch, yaw

# caulk
# cap max z of object obj_z0_s2_0_3

def export_level(game_root, level_name, export_dir, verbose=False):

    bpy.ops.wm.read_factory_settings()

    tex_dir = os.path.join(export_dir, "..", 'textures')
    level_path = os.path.join(game_root, 'LEVELS', 'CAMPAIGN', level_name)
    level_dfs = Dfs()
    level_dfs.open(os.path.join(level_path, 'LEVEL'))
    if verbose:
        print('\n\nLEVEL.DFS contents:\n')
        level_dfs.list_files()

    playsurface = Playsurface()
    playsurface.init(level_dfs.get_file('LEVEL_DATA.PLAYSURFACE'))
    if verbose:
        print('\n\nPlaysurface:\n')
        playsurface.describe()

    level_bin = LevelBin()
    level_bin.init(level_dfs.get_file('LEVEL_DATA.BIN_LEVEL'), level_dfs.get_file('LEVEL_DATA.LEV_DICT'))


    start_pos, start_pitch, start_yaw = loadInfo(level_dfs.get_file('LEVEL_DATA.INFO'))

    col = bpy.data.collections.new("Entities")
    bpy.context.scene.collection.children.link(col)
    obj = bpy.data.objects.new("info_player_spawn_0", None)
    obj["classname"] = "info_player_spawn"
    obj.location = (start_pos[0], start_pos[1] + 320, start_pos[2])
    obj.rotation_euler = (start_pitch, 0, start_yaw)
    col.objects.link(obj)

    resource_dfs = Dfs()
    resource_dfs.open(os.path.join(level_path, 'RESOURCE'))
    if verbose:
        print('\n\nRESOURCE.DFS contents:\n')
        resource_dfs.list_files()

    rigid_geoms = collect_rigid_geoms(playsurface.geoms, resource_dfs, verbose)
    
    set_clips(10, 150000)

    static_geom_collection = bpy.data.collections.new("Static Geometry")
    bpy.context.scene.collection.children.link(static_geom_collection)
    meshes = {}
    materials = {}
    zone_no = 0
    for zone in playsurface.zones:
        col = bpy.data.collections.new("Zone "+str(zone_no))
        static_geom_collection.children.link(col)
        export_surfaces(col, zone, meshes, materials, rigid_geoms, zone_no, tex_dir)
        zone_no += 1
    for zone in playsurface.portals:
        col = bpy.data.collections.new("Portal "+str(zone_no))
        static_geom_collection.children.link(col)
        export_surfaces(col, zone, meshes, materials, rigid_geoms, zone_no, tex_dir)
        zone_no += 1

    remove_mesh("Cube")

    # TODO: caulk y 0 -> 300, x -1930 -> -1470 z -1535

    # Select all objects and scale them by 0.1 to better match doom3 scale
    #bpy.ops.object.select_all(action='SELECT')
    #bpy.ops.transform.resize(value=(0.1, 0.1, 0.1))

    # rotate from y-up to z-up
    #bpy.ops.transform.rotate(value=-1.5708, orient_axis='X')
    #bpy.ops.object.select_all(action='DESELECT')

    bpy.ops.wm.save_as_mainfile(
        filepath=export_dir+'/'+level_name+'.blend', check_existing=False)
