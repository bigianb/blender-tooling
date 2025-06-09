import bpy
import os

from .dfs import Dfs
from .playsurface import Playsurface
from .rigid_geom import RigidGeom
from .geom import Geom


def export_surface(surface, name_prefix, col, meshes, materials, rigid_geoms: list[RigidGeom], tex_dir):
    geom = rigid_geoms[surface.geom_name]
    mesh_no = 0
    for geom_mesh in geom.geom.meshes:
        key = surface.geom_name + geom_mesh.name
        if key in meshes:
            mesh = meshes[key]
        else:
            mesh = bpy.data.meshes.new(key)

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
                
        obj = bpy.data.objects.new(name_prefix + '_' + str(mesh_no), mesh)
        
        if len(geom.geom.textures) > 0:
            # TODO: this is a hack. We should reference the materal used by the mesh.
            # For materials we should use nodes to do it properly.
            texture = geom.geom.textures[0]
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
        bpy.context.view_layer.objects.active = obj
        mesh_no += 1

def export_surfaces(col, zone, meshes, materials, rigid_geoms: list[RigidGeom], zone_no, tex_dir):
    surf_no = 0
    for surface in zone.surfaces:
        export_surface(surface, 'obj_z'+str(zone_no) + '_s'+str(surf_no), col, meshes, materials, rigid_geoms, tex_dir)
        surf_no += 1

def export_level(game_root, level_name, export_dir, verbose=False):

    bpy.ops.wm.read_factory_settings()

    tex_dir = os.path.join(export_dir, "..", 'textures')

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
            if verbose:
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
    materials = {}
    zone_no = 0
    for zone in playsurface.zones:
        col = bpy.data.collections.new("Zone "+str(zone_no))
        bpy.context.scene.collection.children.link(col)
        export_surfaces(col, zone, meshes, materials, rigid_geoms, zone_no, tex_dir)
        zone_no += 1
    for zone in playsurface.portals:
        col = bpy.data.collections.new("Portal "+str(zone_no))
        bpy.context.scene.collection.children.link(col)
        export_surfaces(col, zone, meshes, materials, rigid_geoms, zone_no, tex_dir)
        zone_no += 1

    # remove mesh Cube
    if "Cube" in bpy.data.meshes:
        mesh = bpy.data.meshes["Cube"]
        print("removing mesh", mesh)
        bpy.data.meshes.remove(mesh)

    bpy.ops.wm.save_as_mainfile(
        filepath=export_dir+'/'+level_name+'.blend', check_existing=False)
