import bpy
import bmesh

# ref https://modwiki.dhewm3.org/RBDoom3BFG-Blender-Mapping

def set_clips(near_clip: float, far_clip: float):
    """
    Set the near and far clipping planes for the active camera in Blender.
    
    :param near_clip: The distance to the near clipping plane.
    :param far_clip: The distance to the far clipping plane.
    """

    bpy.context.scene.unit_settings.system = 'NONE'
    screens = (s for w in bpy.data.workspaces for s in w.screens)
    V3Dareas = (a for s in screens for a in s.areas if a.type == 'VIEW_3D')
    V3Dspaces = (s for a in V3Dareas for s in a.spaces if s.type == 'VIEW_3D')
    for space in V3Dspaces:
        space.clip_start = near_clip
        space.clip_end = far_clip

        space.overlay.grid_scale = 10  
        space.overlay.grid_subdivisions = 10
        space.overlay.grid_lines = 1000

        space.overlay.show_floor = True
        space.overlay.show_axis_x = True
        space.overlay.show_axis_y = True
        space.overlay.show_ortho_grid = True


def remove_mesh(mesh_name: str):
    """
    Remove a mesh from Blender by its name.
    
    :param mesh_name: The name of the mesh to remove.
    """
    if mesh_name in bpy.data.meshes:
        mesh = bpy.data.meshes[mesh_name]
        print("Removing mesh", mesh)
        bpy.data.meshes.remove(mesh)
    else:
        print(f"Mesh '{mesh_name}' not found in Blender data."
              )

def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found
        
def activate_collection(collection_name: str):
    """
    Activate a collection in Blender by its name.
    
    :param collection_name: The name of the collection to activate.
    """
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection, collection_name)
    if not layerColl:
        raise ValueError(f"Collection '{collection_name}' not found in Blender data.")
    bpy.context.view_layer.active_layer_collection = layerColl
    
def make_hull_box(collection_name: str, centre_pos, size, name, material):
    activate_collection(collection_name)
    # Inflate the hull by 1% to ensure no leaks
    bpy.ops.mesh.primitive_cube_add(size=1.01, location=centre_pos, scale=size)
    cube = bpy.context.object
    cube.name = name
    cube.active_material = material

    # Flip the normals because we want them to face inwards.
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_mode(type = "FACE")
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    bm.faces.ensure_lookup_table()
    for face_no in range(0, 6):
        bm.faces[face_no].select = True
    bpy.ops.mesh.flip_normals()
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='OBJECT')

