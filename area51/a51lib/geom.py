
from .inev_file import InevFile


class Geom:
    """ Base of rgidgeom or skingeom. """

    valid = False

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
        
        # inevFile.readArray(meshes, numMeshes);
        inev_file.skip(4)
        
        # inevFile.readArray(subMeshes, numSubMeshes);
        inev_file.skip(4)
        
        # inevFile.readArray(materials, numMaterials);
        inev_file.skip(4)
        
        # inevFile.readArray(textures, numTextures);
        inev_file.skip(4)
        
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
        inev_file.skip(4)

        inev_file.skip(4) # Read the unused handle

        self.valid = True

    def is_valid(self):
        return self.valid

    def describe(self):
        if not self.valid:
            print("Geom is not valid")
            return
        print(f'Bounding Box: [{self.bounding_box[0]:.1f}, {self.bounding_box[1]:.1f}, {self.bounding_box[2]:.1f}] -> [{self.bounding_box[4]:.1f}, {self.bounding_box[5]:.1f}, {self.bounding_box[5]:.1f}]')
