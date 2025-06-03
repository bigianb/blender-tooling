import struct

def read_string(file, string_data):
    string_offset = struct.unpack('I', file.read(4))[0]
    output = ''
    while string_data[string_offset] != 0:
        output += chr(string_data[string_offset])
        string_offset += 1
    return output


class Dfs:
    """ A class to deal with DFS files """

    is_valid = False

    def open(self, base_filename):
        """ filename does not include the extension """
        self.base_filename = base_filename
        with open(base_filename+'.DFS', 'rb') as dfsFile:
            self.read_header(dfsFile)

    def read_header(self, dfs_file):
        identifier = dfs_file.read(4).decode('utf-8')
        if identifier != 'SFDX':
            self.is_valid = False
            return
        self.version = struct.unpack('I', dfs_file.read(4))[0]
        if self.version == 3:
            self.checksum = struct.unpack('I', dfs_file.read(4))[0]
        else:
            self.checksum = 0
        self.sector_size = struct.unpack('I', dfs_file.read(4))[0]
        self.split_size = struct.unpack('I', dfs_file.read(4))[0]
        self.num_files = struct.unpack('I', dfs_file.read(4))[0]
        self.num_sub_files = struct.unpack('I', dfs_file.read(4))[0]
        string_len_bytes = struct.unpack('I', dfs_file.read(4))[0]
        self.subfile_offset = struct.unpack('I', dfs_file.read(4))[0]
        file_entry_offset = struct.unpack('I', dfs_file.read(4))[0]
        if self.version == 3:
            self.checksums_offset = struct.unpack('I', dfs_file.read(4))[0]
        strings_offset = struct.unpack('I', dfs_file.read(4))[0]

        dfs_file.seek(strings_offset)
        string_data = dfs_file.read(string_len_bytes)

        self.file_entries = []
        dfs_file.seek(file_entry_offset)
        for _ in range(0, self.num_files):
            entry = {}
            entry['file_name1'] = read_string(dfs_file, string_data)
            entry['file_name2'] = read_string(dfs_file, string_data)
            entry['path_name'] = read_string(dfs_file, string_data)
            entry['ext_name'] = read_string(dfs_file, string_data)
            entry['data_offset'] = struct.unpack('I', dfs_file.read(4))[0]
            entry['data_length'] = struct.unpack('I', dfs_file.read(4))[0]
            self.file_entries.append(entry)

    def list_files(self):
        for entry in self.file_entries:
            name = entry['file_name1'] + \
                entry['file_name2'] + entry['ext_name']
            print(
                f"{name:<32} start:{entry['data_offset']:>8},  length:{entry['data_length']:>8}")

    def get_file(self, sub_filename):
        """ Get the data for a sub-file. Assumes that there is only one data file """
        for entry in self.file_entries:
            if sub_filename == entry['file_name1'] + entry['file_name2'] + entry['ext_name']:
                with open(self.base_filename+'.000', 'rb') as data_file:
                    data_file.seek(entry['data_offset'])
                    return data_file.read(entry['data_length'])
        return None
