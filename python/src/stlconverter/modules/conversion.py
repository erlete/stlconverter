import struct
from pprint import pprint
from time import time

"""BINARY STL

Because ASCII STL files can be very large, a binary version of STL exists. A binary STL file has an 80-character header which is generally ignored, but should never begin with the ASCII representation of the string solid, as that may lead some software to confuse it with an ASCII STL file. Following the header is a 4-byte little-endian unsigned integer indicating the number of triangular facets in the file. Following that is data describing each triangle in turn. The file simply ends after the last triangle.

Each triangle is described by twelve 32-bit floating-point numbers: three for the normal and then three for the X/Y/Z coordinate of each vertex – just as with the ASCII version of STL. After these follows a 2-byte ("short") unsigned integer that is the "attribute byte count" – in the standard format, this should be zero because most software does not understand anything else.[9]

Floating-point numbers are represented as IEEE floating-point numbers and are assumed to be little-endian, although this is not stated in documentation.

UINT8[80]    – Header                 -     80 bytes
UINT32       – Number of triangles    -      4 bytes
foreach triangle                      - 50 bytes:
    REAL32[3] – Normal vector             - 12 bytes
    REAL32[3] – Vertex 1                  - 12 bytes
    REAL32[3] – Vertex 2                  - 12 bytes
    REAL32[3] – Vertex 3                  - 12 bytes
    UINT16    – Attribute byte count      -  2 bytes
end
"""

def c4bytetoIEEE_754_real32(data, step):
    return tuple(
        struct.unpack("<f", data[i:i + 4])[0]
        for i in range(0, len(data), step)
    ) if len(data) != step else (
        struct.unpack("<f", data)[0]
    )

def bytes_to_uint(data):
    return int.from_bytes(data, "little")


class STLTriangle:

    def __init__(self, data):
        self.data = data

    @property
    def normal(self):
        return c4bytetoIEEE_754_real32(self.data[:12], 4)

    @property
    def vertex1(self):
        return c4bytetoIEEE_754_real32(self.data[12:24], 4)

    @property
    def vertex2(self):
        return c4bytetoIEEE_754_real32(self.data[24:36], 4)

    @property
    def vertex3(self):
        return c4bytetoIEEE_754_real32(self.data[36:48], 4)

    @property
    def attribute_byte_count(self):
        return bytes_to_uint(self.data[48:50])

    def __repr__(self):
        return "<STL Triangle>"

    def __str__(self):
        return f"""STL:
    Normal:    {self.normal}
    Vertex 1:  {self.vertex1}
    Vertex 2:  {self.vertex2}
    Vertex 3:  {self.vertex3}
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
        return bytes_to_uint(
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
