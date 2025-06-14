
class InfoHeader:
    type: str
    count: int
    field_defs: list[tuple[str, str]]

class InfoReader:
    """
    A class to read and parse information from a text-based info file.
    """

    def __init__(self, lines):
        self.lines = lines
        self.level_name = ""
        self.level_description = ""
        self.line_no = 0

    def read_header(self) -> InfoHeader:
        """
        Reads the header of the info file to extract level name and description.
        """
        line = ''
        while (self.line_no < len(self.lines) and not line.startswith('[')):
            line = self.lines[self.line_no].strip()
            self.line_no += 1

        if self.line_no >= len(self.lines):
            return None
        
        header = InfoHeader()
        parts = line[1:-1].split(':')
        header.type = parts[0].strip()
        if len(parts) > 1:
            header.count = int(parts[1].strip())
        else:
            header.count = 1

        line = self.lines[self.line_no].strip()
        # expect this line to be like
        # {fieldname1:fieldtype fieldname2:fieldtype ...}
        if not line.startswith('{'):
            raise ValueError(f"Expected field definitions after header, got: {line}")
        fields = line[1:-1].split()
        header.field_defs = []
        for field in fields:
            if ':' not in field:
                raise ValueError(f"Invalid field definition: {field}")
            name, ftype = field.split(':')
            header.field_defs.append((name.strip(), ftype.strip()))
        self.line_no += 1
        
        # There now follow header.count lines of data with the format:
        # field1_value field2_value ...
        header.fields = []
        cur_row = 0
        while cur_row < header.count:
            line = self.lines[self.line_no].strip()
            if (line.startswith('//') or line == ''):
                self.line_no += 1
                continue
            values = line.split()
            header.fields.append(self.decodeRow(values, header.field_defs))
            cur_row += 1
        return header

    def decodeRow(self, values, field_defs):
        decoded = {}
        val_idx = 0
        for name, ftype in field_defs:
            field_values = []
            for data_type in ftype:
                if data_type == 's' or data_type == 'S':
                    field_values.append(values[val_idx])
                    val_idx += 1
                elif data_type == 'd' or data_type == 'D':
                    field_values.append(int(values[val_idx]))
                    val_idx += 1
                elif data_type == 'f' or data_type == 'F':
                    field_values.append(float(values[val_idx]))
                    val_idx += 1
                elif data_type == 'g' or data_type == 'G':
                    value = values[val_idx].replace(':', '').replace('"', '')
                    field_values.append(int(value, 16))  # Assuming hex format
                    val_idx += 1
                else:
                    raise ValueError(f"Unknown data type '{data_type}' in field definition for {name}")
            decoded[name] = field_values if len(field_values) > 1 else field_values[0]
        return decoded
            