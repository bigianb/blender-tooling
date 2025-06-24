import bpy
import os

from a51lib.vecmath import BoundingBox

from .blender_utils import activate_collection, remove_mesh, set_clips, make_hull_box

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
    
class LevelExporter:

    rigid_geoms:  dict[str, RigidGeom]
    materials: dict[str, bpy.types.Material]
    meshes: dict[str, bpy.types.Mesh]
    doom_root: str
    tex_prefix: str
    tex_dir: str
    blend_dir: str
    verbose: bool

    def __init__(self, doom_root: str, verbose: bool):
        self.verbose = verbose
        self.rigid_geoms = {}
        self.materials = {}
        self.meshes = {}
        self.doom_root = doom_root

        self.tex_prefix = 'textures/'
        self.tex_dir = os.path.join(doom_root, 'textures')
        self.blend_dir = os.path.join(doom_root, 'maps')

    def add_door(self, obj: LevelObject, door_collection, door_idx, dfs, geoms):
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
        geom = self.find_rigid_geom(geom_name, dfs, geoms)
        self.export_geom(geom, geom_name, None, pos, rot, door_collection, 'door'+str(door_idx))

    def add_doors(self,level_bin: LevelBin, dfs, geoms):
        door_collection = bpy.data.collections.new("Doors")
        bpy.context.scene.collection.children.link(door_collection)
        door_idx = 1
        for obj in level_bin.objects:
            if obj.type_name == 'Door':
                self.add_door(obj, door_collection, door_idx, dfs, geoms)
                door_idx += 1

    def export_geom(self, geom: RigidGeom, geom_name: str, l2w: list[float], pos, rot, col, name_prefix: str):
        mesh_no = 0
        for geom_mesh in geom.geom.meshes:
            for submesh_idx in range (geom_mesh.idx_sub_mesh, geom_mesh.idx_sub_mesh + geom_mesh.num_sub_meshes):
                submesh = geom.geom.sub_meshes[submesh_idx]
                key = geom_name + '_' + geom_mesh.name + '_' + str(submesh_idx)
                if key in self.meshes:
                    mesh = self.meshes[key]
                else:
                    mesh = bpy.data.meshes.new(key)
                    
                    dlist = geom.dlists[submesh.idx_dlist]
                    verts, faces, uvs = dlist_to_verts_faces(dlist)    

                    mesh.from_pydata(verts, [], faces)
                    self.meshes[key] = mesh

                    uv_data = mesh.uv_layers.new()
                    uv_data.data.foreach_set('uv', uvs)
                        
                obj_name = name_prefix + '_' + str(mesh_no) + '_' + str(submesh_idx)
                obj = bpy.data.objects.new(obj_name, mesh)
                obj["classname"] = "func_static"
                obj["model"] = obj_name
            
                texture_idx = geom.geom.materials[submesh.idx_material].texture_index
                texture = geom.geom.textures[texture_idx]
                if texture.filename in self.materials:
                    material = self.materials[texture.filename]
                else:
                    # https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material
                    tex_basename = texture.filename.split('.')[0].upper()
                    img_path = os.path.join(self.tex_dir, tex_basename+".png")
                    img_path = os.path.abspath(img_path)

                    try:
                        im = bpy.data.images.load(img_path, check_existing=True)
                        im.name = tex_basename+".png"
                    except RuntimeError:
                        im = bpy.data.images.new(tex_basename+".png", 128, 128)
                        # allow the path to be resolved later
                        im.filepath = img_path
                        im.source = 'FILE'

                    material = bpy.data.materials.new(self.tex_prefix+tex_basename)
                    material.use_nodes = True
                    teximage_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                    teximage_node.image = im
                    bsdf_node = material.node_tree.nodes["Principled BSDF"]
                    material.node_tree.links.new(bsdf_node.inputs["Base Color"], teximage_node.outputs["Color"])

                    self.materials[texture.filename] = material
                # for now force the hull material
                obj.active_material = self.materials['textures/base_wall/james'] #material
                
                if l2w:
                    obj.matrix_world = [l2w[i:i+4] for i in range(0, 16, 4)]
                if pos:
                    obj.location = (pos[0], pos[1], pos[2])
                if rot:
                    obj.rotation_euler = (rot[0], rot[1], rot[2])

                col.objects.link(obj)

            mesh_no += 1

    def export_surface(self, surface, name_prefix, col):
        geom = self.rigid_geoms[surface.geom_name]
        self.export_geom(geom, surface.geom_name, surface.l2w, None, None, col, name_prefix)
        
    def export_surfaces(self, col, zone, zone_no):
        surf_no = 0
        for surface in zone.surfaces:
            self.export_surface(surface, 'obj_z'+str(zone_no) + '_s'+str(surf_no), col)
            surf_no += 1

    def find_rigid_geom(self, geom_name: str, dfs: Dfs) -> RigidGeom:
        if geom_name not in self.rigid_geoms:
            geom_data = dfs.get_file(geom_name)
            if geom_data == None:
                print(f'Failed to find data for {geom_name}')
                return None
            geom = RigidGeom()
            geom.read(geom_data)
            if geom.is_valid():
                self.rigid_geoms[geom_name] = geom
            else:
                print(f'Failed to read {geom_name}')
        return self.rigid_geoms[geom_name]

    def collect_rigid_geoms(self, geom_names: list[str], dfs: Dfs) -> None:
        self.rigid_geoms = {}
        for geom_name in geom_names:
            self.find_rigid_geom(geom_name, dfs)


    def export_level(self, game_root: str, level_name: str):

        bpy.ops.wm.read_factory_settings()
        self.meshes = {}
        self.materials = {}
        remove_mesh("Cube")

        level_path = os.path.join(game_root, 'LEVELS', 'CAMPAIGN', level_name)
        level_dfs = Dfs()
        level_dfs.open(os.path.join(level_path, 'LEVEL'))
        if self.verbose:
            print('\n\nLEVEL.DFS contents:\n')
            level_dfs.list_files()

        playsurface = Playsurface()
        playsurface.init(level_dfs.get_file('LEVEL_DATA.PLAYSURFACE'))
        if self.verbose:
            print('\n\nPlaysurface:\n')
            playsurface.describe()

        level_bin = LevelBin()
        level_bin.init(level_dfs.get_file('LEVEL_DATA.BIN_LEVEL'), level_dfs.get_file('LEVEL_DATA.LEV_DICT'))

        start_pos, start_pitch, start_yaw = loadInfo(level_dfs.get_file('LEVEL_DATA.INFO'))

        entities_col = bpy.data.collections.new("Entities")
        bpy.context.scene.collection.children.link(entities_col)

        worldspawn_col = bpy.data.collections.new("Worldspawn")
        bpy.context.scene.collection.children.link(worldspawn_col)
        obj = bpy.data.objects.new("worldspawn", None)
        obj["classname"] = "worldspawn"
        worldspawn_col.objects.link(obj)

        resource_dfs = Dfs()
        resource_dfs.open(os.path.join(level_path, 'RESOURCE'))
        if self.verbose:
            print('\n\nRESOURCE.DFS contents:\n')
            resource_dfs.list_files()

        self.collect_rigid_geoms(playsurface.geoms, resource_dfs)
        
        set_clips(1, 15000)

        static_geom_collection = bpy.data.collections.new("Static Geometry")
        bpy.context.scene.collection.children.link(static_geom_collection)

        hull_material = bpy.data.materials.new('textures/a51/hull')
        self.materials['textures/a51/hull'] = hull_material

        wall_material = bpy.data.materials.new('textures/base_wall/james')
        self.materials['textures/base_wall/james'] = wall_material
        
        zone_no = 0
        for zone in playsurface.zones:
            # For each zone, export the models (surfaces) into the static geometry collection
            # Also create a hull based on the bounding box of the zone in the worldspawn collection
            col = bpy.data.collections.new("Zone "+str(zone_no))
            static_geom_collection.children.link(col)
            self.export_surfaces(col, zone, zone_no)

            hull_bbox = None
            for surface in zone.surfaces:
                if hull_bbox is None:
                    hull_bbox = surface.bounding_box
                else:
                    hull_bbox = hull_bbox.add(surface.bounding_box)
            hull_name = "worldspawn.Zone_" + str(zone_no) + "_Hull"
            make_hull_box(worldspawn_col.name, hull_bbox.centre(), hull_bbox.size(), hull_name, hull_material)

            zone_no += 1
            break   # only export the first zone for now
        # portal_no = 0
        # for zone in playsurface.portals:
        #     col = bpy.data.collections.new("Portal "+str(portal_no))
        #     static_geom_collection.children.link(col)
        #     export_surfaces(col, zone, materials, portal_no, tex_dir, tex_prefix)
        #     portal_no += 1

        #add_doors(level_bin, resource_dfs, materials, tex_dir, tex_prefix)

        obj = bpy.data.objects.new("info_player_spawn_0", None)
        obj["classname"] = "info_player_start"
        obj.location = (start_pos[0], start_pos[1] + 43/0.15, start_pos[2])
        obj.rotation_euler = (start_pitch, 0, start_yaw)
        entities_col.objects.link(obj)

        print(f'{start_pos}' )

        # Select all objects and scale them by 0.1 to better match doom3 scale
        # move player start to the origin
        bpy.ops.object.select_all(action='SELECT')
        
        bpy.ops.transform.resize(value=(0.15, 0.15, 0.15))

        # rotate from y-up to z-up
        bpy.ops.transform.rotate(value=-1.5708, orient_axis='X')
        start_pos = obj.location
        bpy.ops.transform.translate(value=(-start_pos[0], -start_pos[1], -start_pos[2] + 43), orient_type='GLOBAL')  
        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.wm.save_as_mainfile(
            filepath=self.blend_dir+'/'+level_name+'.blend', check_existing=False)
