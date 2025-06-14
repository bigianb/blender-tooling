
from .inev_file import InevFile

class Material:
    detail_scale: float
    fixed_alpha:float
    flags: int
    type: int
    num_textures: int
    texture_index: int

    def __init__(self):
        self.detail_scale = 1.0
        self.fixed_alpha = 1.0
        self.flags = 0
        self.numTextures = 0
        self.texture_index = -1

class Texture:
    filename: str
    description: str
    filename_offset: int
    desc_offset: int
    def __init__(self):
        self.filename = ''

        self.filename_offset = 0
        self.desc_offset = 0

class Mesh:
    bounding_box: list[float]
    name_offset: int
    name: str
    num_sub_meshes: int
    idx_sub_mesh: int
    num_bones: int
    num_faces: int
    num_vertices: int

class SubMesh:
    idx_dlist: int
    idx_material: int
    world_pixel_size: int

class Geom:
    """ Base of rgidgeom or skingeom. """

    valid: bool
    textures: list[Texture]
    materials: list[Material]
    meshes: list[Mesh]
    sub_meshes: list[SubMesh]
    string_data: bytearray

    def __init__(self):
        self.valid = False
        self.bounding_box = [0.0] * 6
        self.textures = []
        self.meshes = []
        self.sub_meshes = []
        self.materials = []

    def read(self, bin_data):
        inev_file = InevFile(bin_data)
        self.valid = inev_file.is_valid()
        if not self.valid:
            return
        self.read_inev(inev_file)

    def read_inev(self, inev_file: InevFile):
        self.bounding_box = inev_file.read_bounding_box()
        self.platform = inev_file.read_i16()
        inev_file.skip(2)
        self.version = inev_file.read_i16()
        self.num_faces = inev_file.read_i16()
        self.num_vertices = inev_file.read_i16()
        self.num_bones = inev_file.read_i16()
        self.num_bone_masks = inev_file.read_i16()
        self.num_property_sections = inev_file.read_i16()
        self.num_properties = inev_file.read_i16()
        self.num_rigid_bodies = inev_file.read_i16()
        self.num_meshes = inev_file.read_i16()
        self.num_sub_meshes = inev_file.read_i16()
        self.num_materials = inev_file.read_i16()
        self.num_textures = inev_file.read_i16()
        self.num_uvkeys = inev_file.read_i16()
        self.num_lods = inev_file.read_i16()
        self.num_virtual_meshes = inev_file.read_i16()
        self.num_virtual_materials = inev_file.read_i16()
        self.num_virtual_textures = inev_file.read_i16()
        self.string_data_size = inev_file.read_i16()

        # inevFile.readArray(bones, numBones);
        inev_file.skip(4)

        # inevFile.readArray(boneMasks, numBoneMasks);
        inev_file.skip(4)

        # inevFile.readArray(propertySections, numPropertySections);
        inev_file.skip(4)

        # inevFile.readArray(properties, numProperties);
        inev_file.skip(4)
        
        # inevFile.readArray(rigidBodies, numRigidBodies);
        inev_file.skip(4)
        
        self._read_meshes(inev_file)
        self._read_submeshes(inev_file)
        self._read_materials(inev_file)
        self._read_textures(inev_file)
                
        # inevFile.readArray(uvKeys, numUVKeys);
        inev_file.skip(4)
        
        # inevFile.readNativeArray(lodSizes, numLODs);
        inev_file.skip(4)

        # inevFile.readNativeArray(lodMasks, numLODs);
        inev_file.skip(4)

        # inevFile.readArray(virtualMeshes, numVirtualMeshes);
        inev_file.skip(4)

        inev_file.skip(4) # Read the unused virtualMaterials pointer.

        # inevFile.readArray(virtualTextures, numVirtualTextures);
        inev_file.skip(4)

        # inevFile.readNativeArray(stringData, stringDataSize);
        array_cursor = inev_file.resolve_pointer(self.string_data_size)
        inev_file.push_cursor(array_cursor)
        self.string_data = inev_file.read_byte_array(self.string_data_size)
        inev_file.pop_cursor()

        inev_file.skip(4) # Read the unused handle

        for tex in self.textures:
            tex.filename = self.lookup_string(tex.filename_offset)
            tex.description = self.lookup_string(tex.desc_offset)

        for mesh in self.meshes:
            mesh.name = self.lookup_string(mesh.name_offset)

        self.valid = True

    def _read_meshes(self, inev_file: InevFile):
        array_cursor = inev_file.resolve_pointer(self.num_meshes)
        inev_file.push_cursor(array_cursor)
        for _ in range(self.num_meshes):
            mesh = Mesh()
            mesh.bounding_box = inev_file.read_bounding_box()
            mesh.name_offset = inev_file.read_i16()
            mesh.num_sub_meshes = inev_file.read_i16()
            mesh.idx_sub_mesh = inev_file.read_i16()
            mesh.num_bones = inev_file.read_i16()
            mesh.num_faces = inev_file.read_i16()
            mesh.num_vertices = inev_file.read_i16()
            inev_file.skip(4)
            self.meshes.append(mesh)
            
        inev_file.pop_cursor()

    def _read_textures(self, inev_file: InevFile):
        array_cursor = inev_file.resolve_pointer(self.num_textures)
        inev_file.push_cursor(array_cursor)
        for _ in range(self.num_textures):
            tex = Texture()
            tex.desc_offset = inev_file.read_i16()
            tex.filename_offset = inev_file.read_i16()

            self.textures.append(tex)
        inev_file.pop_cursor()

    def _read_submeshes(self, inev_file: InevFile):
        array_cursor = inev_file.resolve_pointer(self.num_sub_meshes)
        inev_file.push_cursor(array_cursor)
        for _ in range(self.num_sub_meshes):
            submesh = SubMesh()
            submesh.idx_dlist = inev_file.read_u16()
            submesh.idx_material = inev_file.read_u16()
            submesh.world_pixel_size = inev_file.read_float()

            inev_file.skip(4)
            self.sub_meshes.append(submesh)

        inev_file.pop_cursor()

    def _read_materials(self, inev_file: InevFile):
        array_cursor = inev_file.resolve_pointer(self.num_materials)
        inev_file.push_cursor(array_cursor)
        for _ in range(self.num_materials):
            material = Material()
            inev_file.skip(8)   # skip UV Anim
            material.detail_scale = inev_file.read_float()
            material.fixed_alpha = inev_file.read_float()
            material.flags = inev_file.read_u16()
            material.type = inev_file.read_byte()
            material.num_textures = inev_file.read_byte()
            material.texture_index = inev_file.read_byte()
            inev_file.skip(3)
            self.materials.append(material)
        inev_file.pop_cursor()

    def lookup_string(self, offset):
        """ Lookup a string in the string data. """
        if offset < 0 or offset >= len(self.string_data):
            return ''
        end = self.string_data.find(0, offset)
        if end == -1:
            end = len(self.string_data)
        return self.string_data[offset:end].decode('utf-8')

    def is_valid(self):
        return self.valid

    def describe(self):
        if not self.valid:
            print("Geom is not valid")
            return
        print(f'Bounding Box: [{self.bounding_box[0]:.1f}, {self.bounding_box[1]:.1f}, {self.bounding_box[2]:.1f}] -> [{self.bounding_box[4]:.1f}, {self.bounding_box[5]:.1f}, {self.bounding_box[5]:.1f}]')
