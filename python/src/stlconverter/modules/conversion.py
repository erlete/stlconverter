"""Conversion module.

This module contains all required classes and methods to convert STL files
between ASCII and binary formats (and vice versa).

Notes:
    STL binary uses little-endian byte order and IEEE-754 floating-point
    standard. Below are two examples of STL files, one in binary and the other
    in ASCII format (from Wikipedia):

    STL (binary) file structure:

        UINT8[80]        - Header               - 80 bytes
        UINT32           - Number of triangles  -  4 bytes
        foreach triangle - (50 bytes)
            REAL32[3]    - Normal vector        - 12 bytes
            REAL32[3]    - Vertex 1             - 12 bytes
            REAL32[3]    - Vertex 2             - 12 bytes
            REAL32[3]    - Vertex 3             - 12 bytes
            UINT16       - Attribute byte count -  2 bytes
        end              - N/A
        ...

    STLA (ASCII) file structure:

        solid <name>
            facet normal <ni> <nj> <nk>
                outer loop
                    vertex <v1x> <v1y> <v1z>
                    vertex <v2x> <v2y> <v2z>
                    vertex <v3x> <v3y> <v3z>
                endloop
            endfacet
            ...
        endsolid <name>

Author:
    Paulo Sanchez (@erlete)
"""


import struct
from typing import Tuple


class ByteConversion:
    """Byte conversion class.

    This class contains several methods for converting bytes to other data
    types, such as IEEE-754 floating-point numbers and unsigned integers.
    """

    @staticmethod
    def bytes_to_real32(byte_quad: bytes) -> float:
        """Convert byte quadruplet to IEEE-754 floating-point number.

        Args:
            byte_quad (bytes): Byte quadruplet to be converted.

        Returns:
            float: IEEE-754 floating-point number.
        """
        return struct.unpack("<f", byte_quad)[0]

    @staticmethod
    def byte_coord_to_real32(byte_coord: bytes) -> Tuple[float, ...]:
        """Convert byte-based 3D coordinate to IEEE-754 floating-point number.

        Args:
            byte_coord (bytes): Byte-based 3D coordinate to be converted.

        Returns:
            Tuple[Float, Float, Float]: IEEE-754 floating-point 3D coordinate.
        """
        return tuple(
            ByteConversion.bytes_to_real32(byte_coord[i:i + 4])
            for i in range(0, len(byte_coord), 4)
        )

    @staticmethod
    def bytes_to_uint(byte_data: bytes) -> int:
        """Convert byte value to unsigned integer.

        Args:
            byte_data (bytes): Byte value to be converted.

        Returns:
            int: Unsigned integer.
        """
        return int.from_bytes(byte_data, "little")


class STLTriangle:

    _STOPS = {
        "normal": 12,
        "vertex1": 24,
        "vertex2": 36,
        "vertex3": 48,
        "attribute": 50
    }

    def __init__(self, byte_data):
        self.byte_data = byte_data

    @property
    def normal(self):
        return ByteConversion.byte_coord_to_real32(
            self.byte_data[:self._STOPS["normal"]]
        )

    @property
    def vertices(self):
        step = self._STOPS["vertex2"] - self._STOPS["vertex1"]
        return tuple(
            ByteConversion.byte_coord_to_real32(self.byte_data[i:i + step])
            for i in range(self._STOPS["normal"], self._STOPS["vertex3"], step)
        )

    @property
    def attribute_byte_count(self):
        return ByteConversion.bytes_to_uint(self.byte_data[48:50])

    def __repr__(self):
        return "<STL Triangle>"

    def __str__(self):
        vertices = "\n    ".join(
            f"Vertex {i + 1}:  {vertex}"
            for i, vertex in enumerate(self.vertices)
        )
        return f"""STL Triangle:
    Normal:    {self.normal}
    {vertices}
    Attribute: {self.attribute_byte_count}"""

class STL:
    _STOPS = {
        "header": 80,
        "ntriangles": 84
    }

    def __init__(self, data):
        self.data = data

    @property
    def header(self):
        return self.data[:self._STOPS["header"]].strip(b"\x00").decode("ASCII")

    @property
    def ntriangles(self):
        return ByteConversion.bytes_to_uint(
            self.data[self._STOPS["header"]:self._STOPS["ntriangles"]]
        )

    def __repr__(self):
        return f"<STL with {self.ntriangles} triangles>"

    def __str__(self):
        return f"""STL:
    Header:    {self.header}
    Triangles: {self.ntriangles}"""


with open("stl.stl", mode="rb") as fp:
    data = fp.read()

stl = STL(data)
print(stl)
print([stl])

triangles = [
    STLTriangle(data[i:i + 50])
    for i in range(84, len(data), 50)
]

print(triangles[0])

st = ""
st += f"solid {stl.header}\n"
for triangle in triangles:
    st += f"  facet normal {' '.join(str(val) for val in triangle.normal).strip()}\n"
    st += "    outer loop\n"
    st += f"      vertex {' '.join(str(val) for val in triangle.vertex1).strip()}\n"
    st += f"      vertex {' '.join(str(val) for val in triangle.vertex2).strip()}\n"
    st += f"      vertex {' '.join(str(val) for val in triangle.vertex3).strip()}\n"
    st += "    endloop\n"
    st += "  endfacet\n"

st += f"endsolid {stl.header}"

with open(f"OUT_STL_ASCII_{time()}.stl", mode="w") as fp:
    fp.write(st)
