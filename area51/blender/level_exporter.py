import bpy
import os

from a51lib.vecmath import BoundingBox

from .blender_utils import activate_collection, remove_mesh, set_clips

from a51lib.info_reader import InfoReader

from a51lib.dfs import Dfs
from a51lib.playsurface import Playsurface
from a51lib.rigid_geom import RigidGeom
from a51lib.level_bin import LevelBin, LevelObject

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

def add_door(obj: LevelObject, door_collection, door_idx, dfs, geoms, meshes, materials, tex_dir, tex_prefix):
    # Example Door properties:
    #
    # Base\Position = [-1700.0, 0.0, -3150.0]
    # Base\Rotation = [0.0, 1.5707964897155762, 0.0]
    # RenderInst\File = AH_HangarDoor_4x4m_000_bindpose.rigidgeom
    # Door\Initial State = CLOSED
    # Door\Resting State = CLOSED
    geom_name = obj.properties['RenderInst\\File']
    pos = obj.properties['Base\\Position']
    rot = obj.properties['Base\\Rotation']
    geom = find_rigid_geom(geom_name, dfs, geoms)
    export_geom(geom, geom_name, None, pos, rot, door_collection, meshes, materials, 'door'+str(door_idx), tex_dir, tex_prefix)

def add_doors(level_bin: LevelBin, dfs, geoms, meshes, materials, tex_dir, tex_prefix):
    door_collection = bpy.data.collections.new("Doors")
    bpy.context.scene.collection.children.link(door_collection)
    door_idx = 1
    for obj in level_bin.objects:
        if obj.type_name == 'Door':
            add_door(obj, door_collection, door_idx, dfs, geoms, meshes, materials, tex_dir, tex_prefix)
            door_idx += 1

def export_geom(geom: RigidGeom, geom_name: str, l2w: list[float], pos, rot, col, meshes, materials, name_prefix: str, tex_dir: str, tex_prefix: str):
    mesh_no = 0
    for geom_mesh in geom.geom.meshes:
        for submesh_idx in range (geom_mesh.idx_sub_mesh, geom_mesh.idx_sub_mesh + geom_mesh.num_sub_meshes):
            submesh = geom.geom.sub_meshes[submesh_idx]
            key = geom_name + '_' + geom_mesh.name + '_' + str(submesh_idx)
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

                material = bpy.data.materials.new(tex_prefix+tex_basename)
                material.use_nodes = True
                teximage_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                teximage_node.image = im
                bsdf_node = material.node_tree.nodes["Principled BSDF"]
                material.node_tree.links.new(bsdf_node.inputs["Base Color"], teximage_node.outputs["Color"])

                materials[texture.filename] = material
            # for now force the hull material
            obj.active_material = materials['textures/a51/hull'] #material
            if l2w:
                obj.matrix_world = [l2w[i:i+4] for i in range(0, 16, 4)]
            if pos:
                obj.location = (pos[0], pos[1], pos[2])
            if rot:
                obj.rotation_euler = (rot[0], rot[1], rot[2])

            col.objects.link(obj)

        mesh_no += 1

def export_surface(surface, name_prefix, col, meshes, materials, rigid_geoms: list[RigidGeom], tex_dir, tex_prefix):
    geom = rigid_geoms[surface.geom_name]
    export_geom(geom, surface.geom_name, surface.l2w, None, None, col, meshes, materials, name_prefix, tex_dir, tex_prefix)
    
def export_surfaces(col, zone, meshes, materials, rigid_geoms: list[RigidGeom], zone_no, tex_dir, tex_prefix):
    surf_no = 0
    for surface in zone.surfaces:
        export_surface(surface, 'obj_z'+str(zone_no) + '_s'+str(surf_no), col, meshes, materials, rigid_geoms, tex_dir, tex_prefix)
        surf_no += 1

def find_rigid_geom(geom_name: str, dfs: Dfs, geom_repo: dict[str, RigidGeom]) -> RigidGeom:
    if geom_name not in geom_repo:
        geom_data = dfs.get_file(geom_name)
        if geom_data == None:
            print(f'Failed to find data for {geom_name}')
            return None
        geom = RigidGeom()
        geom.read(geom_data)
        if geom.is_valid():
            geom_repo[geom_name] = geom
        else:
            print(f'Failed to read {geom_name}')
    return geom_repo[geom_name]

def collect_rigid_geoms(geom_names: list[str], dfs: Dfs) -> dict[str, RigidGeom]:
    rigid_geoms = {}
    for geom_name in geom_names:
        find_rigid_geom(geom_name, dfs, rigid_geoms)
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

def create_bbox_mesh(bbox: list[float]):
    verts = []
    faces = []

    min_x = bbox[0]
    min_y = bbox[1]
    min_z = bbox[2]
    max_x = bbox[3]
    max_y = bbox[4]
    max_z = bbox[5]

    if min_z == max_z:
        verts = [[min_x, min_y, min_z], [max_x, min_y, min_z], [min_x, max_y, min_z], [max_x, max_y, min_z]]
        faces = [(0, 1, 2), (1, 3, 2)]
    elif min_y == max_y:
        verts = [[min_x, min_y, min_z], [max_x, min_y, min_z], [min_x, min_y, max_z], [max_x, min_y, max_z]]
        faces = [(0, 1, 2), (1, 3, 2)]
    else:
        raise ValueError("Bounding Box configuration not yet supported")

    return verts, faces

def export_level(game_root: str, level_name: str, doom_root: str, caulk: list[list[float]], verbose=False):

    bpy.ops.wm.read_factory_settings()
    remove_mesh("Cube")

    tex_prefix = 'textures/'
    tex_dir = os.path.join(doom_root, 'textures')
    blend_dir = os.path.join(doom_root, 'maps')
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
    obj["classname"] = "info_player_start"
    obj.location = (start_pos[0], start_pos[1] + 320, start_pos[2])
    obj.rotation_euler = (start_pitch, 0, start_yaw)
    col.objects.link(obj)

    worldspawn_col = bpy.data.collections.new("Worldspawn")
    bpy.context.scene.collection.children.link(worldspawn_col)
    obj = bpy.data.objects.new("worldspawn", None)
    obj["classname"] = "worldspawn"
    worldspawn_col.objects.link(obj)

    resource_dfs = Dfs()
    resource_dfs.open(os.path.join(level_path, 'RESOURCE'))
    if verbose:
        print('\n\nRESOURCE.DFS contents:\n')
        resource_dfs.list_files()

    rigid_geoms = collect_rigid_geoms(playsurface.geoms, resource_dfs)
    
    set_clips(10, 150000)

    static_geom_collection = bpy.data.collections.new("Static Geometry")
    bpy.context.scene.collection.children.link(static_geom_collection)
    meshes = {}
    materials = {}
    hull_material = bpy.data.materials.new('textures/a51/hull')
    materials['textures/a51/hull'] = hull_material
    zone_no = 0
    for zone in playsurface.zones:
        # For each zone, export the models (surfaces) into the static geometry collection
        # Also create a hull based on the bounding box of the zone in the worldspawn collection
        col = bpy.data.collections.new("Zone "+str(zone_no))
        static_geom_collection.children.link(col)
        export_surfaces(col, zone, meshes, materials, rigid_geoms, zone_no, tex_dir, tex_prefix)

        hull_bbox = None
        for surface in zone.surfaces:
            if hull_bbox is None:
                hull_bbox = surface.bounding_box
            else:
                hull_bbox = hull_bbox.add(surface.bounding_box)

        activate_collection(worldspawn_col.name)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=hull_bbox.centre(), scale=hull_bbox.size())
        cube = bpy.context.object
        cube.name = "worldspawn.Zone_" + str(zone_no) + "_Hull"
        cube.active_material = hull_material

        zone_no += 1
        break   # only export the first zone for now
    # portal_no = 0
    # for zone in playsurface.portals:
    #     col = bpy.data.collections.new("Portal "+str(portal_no))
    #     static_geom_collection.children.link(col)
    #     export_surfaces(col, zone, meshes, materials, rigid_geoms, portal_no, tex_dir, tex_prefix)
    #     portal_no += 1



    #add_doors(level_bin, resource_dfs, rigid_geoms, meshes, materials, tex_dir, tex_prefix)

    if len(caulk) > 0:
        # material textures/common/caulk
        caulk_material = bpy.data.materials.new('textures/common/caulk')
        caulk_collection = bpy.data.collections.new("Caulk")
        bpy.context.scene.collection.children.link(caulk_collection)
        for caulk_idx in range(0, len(caulk)):
            mesh = bpy.data.meshes.new("caulk_"+str(caulk_idx))
            verts, faces = create_bbox_mesh(caulk[caulk_idx])
            mesh.from_pydata(verts, [], faces)
            obj = bpy.data.objects.new("caulk_"+str(caulk_idx), mesh)
            obj.active_material = caulk_material
            caulk_collection.objects.link(obj)

    # Select all objects and scale them by 0.1 to better match doom3 scale
    #bpy.ops.object.select_all(action='SELECT')
    #bpy.ops.transform.resize(value=(0.1, 0.1, 0.1))

    # rotate from y-up to z-up
    #bpy.ops.transform.rotate(value=-1.5708, orient_axis='X')
    #bpy.ops.object.select_all(action='DESELECT')

    bpy.ops.wm.save_as_mainfile(
        filepath=blend_dir+'/'+level_name+'.blend', check_existing=False)
