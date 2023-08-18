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


class BinarySTLTriangle:
    """STL Triangle representation class.

    This class represents a single triangle in an STL file. It contains the
    triangle's normal vector, its three vertices and the attribute byte count.

    Attributes:
        byte_data (bytes): Byte data of the triangle.

    Properties:
        normal (Tuple[float, ...]): Normal vector of the triangle.
        vertices (Tuple[Tuple[float, ...], ...]): Vertices of the
            triangle.
        attribute_byte_count (int): Attribute byte count of the triangle.
    """

    _STOPS = {
        "normal": 12,
        "vertex1": 24,
        "vertex2": 36,
        "vertex3": 48,
        "attribute": 50
    }

    def __init__(self, byte_data: bytes) -> None:
        """Initialize a BinarySTLTriangle instance.

        Args:
            byte_data (bytes): Byte data of the triangle.
        """
        self.byte_data = byte_data

    @property
    def normal(self) -> Tuple[float, ...]:
        """Get the normal vector of the triangle.

        Returns:
            Tuple[float, ...]: Normal vector of the triangle.
        """
        return ByteConversion.byte_coord_to_real32(
            self.byte_data[:self._STOPS["normal"]]
        )

    @property
    def vertices(self) -> Tuple[Tuple[float, ...], ...]:
        """Get the vertices of the triangle.

        Returns:
            Tuple[Tuple[float, ...], ...]: Vertices of the triangle.
        """
        step = self._STOPS["vertex2"] - self._STOPS["vertex1"]
        return tuple(
            ByteConversion.byte_coord_to_real32(self.byte_data[i:i + step])
            for i in range(self._STOPS["normal"], self._STOPS["vertex3"], step)
        )

    @property
    def attribute_byte_count(self) -> int:
        """Get the attribute byte count of the triangle.

        Returns:
            int: Attribute byte count of the triangle.
        """
        return ByteConversion.bytes_to_uint(self.byte_data[48:50])

    def __repr__(self) -> str:
        """Get the raw representation of the triangle.

        Returns:
            str: Raw representation of the triangle.
        """
        return "<STL Triangle>"

    def __str__(self) -> str:
        """Get the extended representation of the triangle.

        Returns:
            str: Extended representation of the triangle.
        """
        vertices = "\n    ".join(
            f"Vertex {i + 1}:  {vertex}"
            for i, vertex in enumerate(self.vertices)
        )
        return f"""STL Triangle:
    Normal:    {self.normal}
    {vertices}
    Attribute: {self.attribute_byte_count}"""


class BinarySTL:
    """Binary STL file representation class.

    Attributes:
        byte_data (bytes): Byte data of the STL file.

    Properties:
        header (str): Header of the STL file.
        ntriangles (int): Number of triangles in the STL file.
        triangles (Tuple[BinarySTLTriangle, ...]): Triangles in the STL file.
    """

    _STOPS = {
        "header": 80,
        "ntriangles": 84
    }

    def __init__(self, byte_data: bytes) -> None:
        """Initialize a STL instance.

        Args:
            byte_data (bytes): Byte data of the STL file.
        """
        self.byte_data = byte_data

    @property
    def header(self) -> str:
        """Get the header of the STL file.

        Returns:
            str: Header of the STL file.
        """
        return self.byte_data[:self._STOPS["header"]].strip(b"\x00").decode(
            "ASCII"
        )

    @property
    def ntriangles(self) -> int:
        """Get the number of triangles in the STL file.

        Returns:
            int: Number of triangles in the STL file.
        """
        return ByteConversion.bytes_to_uint(
            self.byte_data[self._STOPS["header"]:self._STOPS["ntriangles"]]
        )

    @property
    def triangles(self) -> Tuple[BinarySTLTriangle, ...]:
        """Get the triangles in the STL file.

        Returns:
            Tuple[BinarySTLTriangle, ...]: Triangles in the STL file.
        """
        return tuple(
            BinarySTLTriangle(self.byte_data[i:i + 50])
            for i in range(self._STOPS["ntriangles"], len(self.byte_data), 50)
        )

    def __repr__(self) -> str:
        """Get the raw representation of the STL file.

        Returns:
            str: Raw representation of the STL file.
        """
        return f"<STL with {self.ntriangles} triangles>"

    def __str__(self) -> str:
        """Get the extended representation of the STL file.

        Returns:
            str: Extended representation of the STL file.
        """
        return f"""STL:
    Header:    {self.header}
    Triangles: {self.ntriangles}"""


class ASCIISTLTriangle:
    """STL Triangle representation class.

    This class represents a single triangle in an STL file. It contains the
    triangle's normal vector, its three vertices and the attribute byte count.

    Attributes:
        lines (Tuple[str, ...]): Lines of the triangle.

    Properties:
        normal (Tuple[float, ...]): Normal vector of the triangle.
        vertices (Tuple[Tuple[float, ...], ...]): Vertices of the
            triangle.
    """

    def __init__(self, lines: Tuple[str, ...]) -> None:
        """Initialize an ASCIISTLTriangle instance.

        Args:
            lines (Tuple[str, ...]): Lines of the triangle.
        """
        self.lines = lines

    @property
    def normal(self) -> Tuple[float, ...]:
        """Get the normal vector of the triangle.

        Returns:
            Tuple[float, ...]: Normal vector of the triangle.
        """
        return tuple(
            float(val)
            for val in self.lines[1].strip("facet normal").strip().split()
        )

    @property
    def vertices(self) -> Tuple[Tuple[float, ...], ...]:
        """Get the vertices of the triangle.

        Returns:
            Tuple[Tuple[float, ...], ...]: Vertices of the triangle.
        """
        return tuple(
            tuple(
                float(val)
                for val in line.strip("vertex").strip().split()
            )
            for line in self.lines[2:5]
        )

    def __repr__(self) -> str:
        """Get the raw representation of the triangle.

        Returns:
            str: Raw representation of the triangle.
        """
        return "<STL Triangle>"

    def __str__(self) -> str:
        """Get the extended representation of the triangle.

        Returns:
            str: Extended representation of the triangle.
        """
        vertices = "\n    ".join(
            f"Vertex {i + 1}:  {vertex}"
            for i, vertex in enumerate(self.vertices)
        )
        return f"""STL Triangle:
    Normal:    {self.normal}
    {vertices}"""


class ASCIISTL:
    """ASCII STL file representation class.

    Attributes:
        ascii_data (str): ASCII data of the STL file.

    Properties:
        header (str): Header of the STL file.
        ntriangles (int): Number of triangles in the STL file.
        triangles (Tuple[BinarySTLTriangle, ...]): Triangles in the STL file.
    """

    def __init__(self, ascii_data: str) -> None:
        """Initialize a STL instance.

        Args:
            ascii_data (str): ASCII data of the STL file.
        """
        self.ascii_data = ascii_data
        self.lines = ascii_data.split("\n")

    @property
    def header(self) -> str:
        """Get the header of the STL file.

        Returns:
            str: Header of the STL file.
        """
        return self.lines[0].strip("solid").strip()

    @property
    def ntriangles(self) -> int:
        """Get the number of triangles in the STL file.

        Returns:
            int: Number of triangles in the STL file.
        """
        return len(self.triangles)

    @property
    def triangles(self) -> Tuple[ASCIISTLTriangle, ...]:
        """Get the triangles in the STL file.

        Returns:
            Tuple[ASCIISTLTriangle, ...]: Triangles in the STL file.
        """
        triangles = []
        for i, line in enumerate(self.lines):
            if line.strip().startswith("facet normal"):
                triangles.append(
                    ASCIISTLTriangle(tuple(self.lines[i:i + 5]))
                )
        return tuple(triangles)

    def __repr__(self) -> str:
        """Get the raw representation of the STL file.

        Returns:
            str: Raw representation of the STL file.
        """
        return f"<STL with {self.ntriangles} triangles>"

    def __str__(self) -> str:
        """Get the extended representation of the STL file.

        Returns:
            str: Extended representation of the STL file.
        """
        return f"""STL:
    Header:    {self.header}
    Triangles: {self.ntriangles}"""
