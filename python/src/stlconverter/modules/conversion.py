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
from typing import Any, Dict, Tuple, Union


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


class Reader:
    """Generic reader interface class."""

    @classmethod
    def _read_stlb(cls, data: bytes) -> Dict[str, Any]:
        """Read STL binary data.

        Args:
            data (bytes): STL binary data.

        Returns:
            Dict[str, Any]: normalized transition data.
        """
        return {}

    @classmethod
    def _read_stla(cls, data: str) -> Dict[str, Any]:
        """Read STL ASCII data.

        Args:
            data (str): STL ASCII data.

        Returns:
            Dict[str, Any]: normalized transition data.
        """
        return {}

    @classmethod
    def read(cls, data: Union[bytes, str]) -> Dict[str, Any]:
        """Interface reading method.

        Args:
            data (Union[bytes, str]): STL data (either ASCII or binary).

        Raises:
            TypeError: if data is not a type "bytes" or "str".

        Returns:
            Dict[str, Any]: normalized transition data.
        """
        if isinstance(data, bytes):
            return cls._read_stlb(data)
        elif isinstance(data, str):
            return cls._read_stla(data)
        else:
            raise TypeError("data must be a type \"bytes\" or \"str\"")


class TriangleReader(Reader):
    """Specific implementation of the Reader interface for STL triangles.

    This class is responsible for reading STL triangle data, which is composed
    of a normal vector, three vertices and an attribute byte count. After
    reading the data, it is stored in a transition dictionary, which follows
    the following structure:

        {
            "normal": Tuple[Float, Float, Float],
            "vertices": Tuple[Tuple[Float, Float, Float], ...],
            "attribute": Int
        }
    """

    @classmethod
    def _read_stlb(cls, data: bytes) -> Dict[str, Any]:
        return {
            "normal": ByteConversion.byte_coord_to_real32(data[:12]),
            "vertices": tuple(
                ByteConversion.byte_coord_to_real32(data[i:i + 12])
                for i in range(12, 48, 12)
            ),
            "attribute": ByteConversion.bytes_to_uint(data[48:50])
        }

    @classmethod
    def _read_stla(cls, data: str) -> Dict[str, Any]:
        lines = [line.strip() for line in data.strip().split("\n")]
        return {
            "normal": tuple(
                float(val.strip())
                for val in lines[0].strip("facet normal").strip().split()
            ),
            "vertices": tuple(
                tuple(
                    float(val.strip())
                    for val in line.strip("vertex").strip().split()
                )
                for line in lines[2:5]
            ),
            "attribute": 0
        }


class FileReader(Reader):
    """Specific implementation of the Reader interface for STL files.

    This class is responsible for reading STL file data, which is composed of
    a header, the number of triangles and the triangles themselves. After
    reading the data, it is stored in a transition dictionary, which follows
    the following structure:

        {
            "header": String,
            "n_triangles": Int,
            "triangles": Tuple[Dict[str, Any], ...]
        }
    """

    @classmethod
    def _read_stlb(cls, data: bytes) -> Dict[str, Any]:
        return {
            "header": data[:80].strip(b"\x00").decode("ASCII"),
            "n_triangles": ByteConversion.bytes_to_uint(data[80:84]),
            "triangles": tuple(
                TriangleReader.read(data[i:i + 50])
                for i in range(84, len(data), 50)
            )
        }

    @classmethod
    def _read_stla(cls, data: str) -> Dict[str, Any]:
        lines = [line.strip() for line in data.strip().split("\n")]
        return {
            "header": lines[0].strip("solid").strip(),
            "n_triangles": (len(lines) - 1) // 7,
            "triangles": tuple([
                TriangleReader.read("\n".join(lines[i:i + 5]))  # Skip 2 lines
                for i, line in enumerate(lines)
                if line.strip().startswith("facet normal")
            ])
        }


class STL:
    """STL file structural class.

    This class is responsible for reading and storing STL file transition
    data so that it can be easily exported to STL ASCII or binary formats.

    Properties:
        header (str): STL file header.
        n_triangles (int): number of triangles in the STL file.
        triangles (Tuple[Dict[str, Any], ...]): triangles in the STL file.
    """

    _INDENTATION_SPACES = 2

    def __init__(self, path: str) -> None:
        """Initialize an STL instance.

        Args:
            path (str): path to the STL file.
        """
        with open(path, mode="rb") as fp:
            data = fp.read()

        if data.isascii():
            self.data = FileReader.read(data.decode("utf-8"))
        else:
            self.data = FileReader.read(data)

        # Set attributes for property access:
        self._header = self.data["header"]
        self._n_triangles = self.data["n_triangles"]
        self._triangles = self.data["triangles"]

        # Extra attributes:
        self._is_input_binary = not data.isascii()
        self._is_input_ascii = data.isascii()

    @property
    def header(self) -> str:
        """Get STL file header.

        Returns:
            str: STL file header.
        """
        return self._header

    @property
    def n_triangles(self) -> int:
        """Get number of triangles in the STL file.

        Returns:
            int: number of triangles in the STL file.
        """
        return self._n_triangles

    @property
    def triangles(self) -> Tuple[Dict[str, Any], ...]:
        """Get triangles in the STL file.

        Returns:
            Tuple[Dict[str, Any], ...]: triangles in the STL file.
        """
        return self._triangles

    def _indent(self, text: str, level: int) -> str:
        """Indent text using `STL._INDENTATION_SPACES`.

        Args:
            text (str): text to be indented.
            level (int): indentation level.

        Returns:
            str: indented text.
        """
        return f"{self._INDENTATION_SPACES * level * ' '}{text}"

    def to_stlb(self) -> bytes:
        """Convert STL data to STL binary format.

        Returns:
            bytes: STL binary data.
        """
        header = self.data["header"].encode("ASCII")
        output = header + b"\x00" * (80 - len(header))
        output += struct.pack("<I", self.data["n_triangles"])
        for triangle in self.data["triangles"]:
            output += struct.pack("<fff", *triangle["normal"])
            for vertex in triangle["vertices"]:
                output += struct.pack("<fff", *vertex)
            output += struct.pack("<H", triangle["attribute"])

        return output

    def to_stla(self) -> str:
        """Convert STL data to STL ASCII format.

        Returns:
            str: STL ASCII data.
        """
        output = f"solid {self.header}\n"
        for triangle in self.triangles:
            normal = " ".join(str(val) for val in triangle['normal']).strip()
            output += self._indent(f"facet normal {normal}\n", 1)
            output += self._indent("outer loop\n", 2)
            output += "\n".join(
                self._indent(
                    f"vertex {' '.join(str(val) for val in vertex).strip()}",
                    3
                ) for vertex in triangle["vertices"]
            ) + "\n"
            output += self._indent("endloop\n", 2)
            output += self._indent("endfacet\n", 1)

        output += f"endsolid {self.header}"
        return output

    def save_stlb(self, path: str) -> None:
        """Save STL data to STL binary format.

        Args:
            path (str): path to the STL binary file.
        """
        with open(path, mode="wb") as fp:
            fp.write(self.to_stlb())

    def save_stla(self, path: str) -> None:
        """Save STL data to STL ASCII format.

        Args:
            path (str): path to the STL ASCII file.
        """
        with open(path, mode="w", encoding="utf-8") as fp:
            fp.write(self.to_stla())
