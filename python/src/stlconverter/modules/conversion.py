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

    @classmethod
    def _read_stlb(cls, data: bytes) -> Dict[str, Any]:
        pass

    @classmethod
    def _read_stla(cls, data: str) -> Dict[str, Any]:
        pass

    @classmethod
    def read(cls, data: Union[bytes, str]) -> Dict[str, Any]:
        if isinstance(data, bytes):
            return cls._read_stlb(data)
        elif isinstance(data, str):
            return cls._read_stla(data)
        else:
            raise TypeError("data must be a type \"bytes\" or \"str\"")


class TriangleReader(Reader):

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

    def __init__(self, data: Union[bytes, str]) -> None:
        self.data = FileReader.read(data)

    def to_stlb(self) -> bytes:
        pass

    def to_stla(self) -> str:
        pass
