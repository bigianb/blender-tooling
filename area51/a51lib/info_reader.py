
class InfoHeader:
    type: str
    count: int

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
        #expect this line to be like
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
        
        return header
