class Employee:
    def __init__(self, idx, id, name, position, department):
        self.idx = idx
        self.id = id
        self.name = name
        self.position = position
        self.department = department

    @classmethod
    def from_string(cls, string):
        parts = string.split()
        return cls(
            idx=parts[0],
            name=parts[1],
            id=parts[3],
            position=parts[5],
            department=parts[13]
        )
