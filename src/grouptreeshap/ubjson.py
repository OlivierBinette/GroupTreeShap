import struct
from io import BytesIO, SEEK_CUR
from typing import Union, BinaryIO, Optional


class UBJSONDecodeError(Exception):
    pass

class UBJSONUnsupportedError(UBJSONDecodeError):
    pass


class UBJSONDecoder:
    _JTYPE = Union[None, bytes, tuple[bytes, Union[None, tuple['_JTYPE', int]]]]
    def __init__(self, byte_stream: Union[bytes, BinaryIO]):
        if isinstance(byte_stream, (bytes, bytearray)):
            byte_stream = BytesIO(byte_stream)
        elif not hasattr(byte_stream, "read"):
            raise TypeError("Expected bytes, bytearray, or a binary file-like object")
        self.fp: BinaryIO = byte_stream

    def decode(self) -> object:
        return self._decode_from_type(None)

    def _read_exact(self, n: int) -> bytes:
        data = self.fp.read(n)
        if len(data) != n:
            raise UBJSONDecodeError(
                f"Unexpected end of stream. Expected {n} bytes, got {len(data)}."
            )
        return data

    def _decode_from_type(self, jtype:_JTYPE) -> object:
        match jtype:
            case None: return self._decode_from_type(self._parse_type())
            case (b'[', array_type): return self._decode_array(array_type)
            case (b'{', object_type): return self._decode_object(object_type)

        # treat jtype as marker
        return self._decode_by_marker(jtype)

    def _decode_by_marker(self, marker: bytes) -> object:
        parser = {
            b"Z": lambda: None,
            b"T": lambda: True,
            b"F": lambda: False,
            b"i": lambda: struct.unpack(">b", self._read_exact(1))[0],
            b"U": lambda: struct.unpack(">B", self._read_exact(1))[0],
            b"I": lambda: struct.unpack(">h", self._read_exact(2))[0],
            b"l": lambda: struct.unpack(">i", self._read_exact(4))[0],
            b"L": lambda: struct.unpack(">q", self._read_exact(8))[0],
            b"d": lambda: struct.unpack(">f", self._read_exact(4))[0],
            b"D": lambda: struct.unpack(">d", self._read_exact(8))[0],
            b"C": lambda: self._read_exact(1).decode("utf-8"),
            b"S": lambda: self._decode_string(),
            b"H": lambda: self._decode_string(),
        }.get(marker)

        if parser is not None:
            return parser()
        elif marker is b'N':
            raise UBJSONDecodeError(f"Unimplemented marker: {marker}")
        else:
            raise UBJSONDecodeError(f"Unknown marker: {marker}")

    def _decode_string(self) -> str:
        length = self._decode_length()
        return self._read_exact(length).decode("utf-8")

    def _decode_length(self) -> int:
        type_marker = self.fp.read(1)

        length = {
            b"U": lambda: struct.unpack(">B", self._read_exact(1))[0],
            b"i": lambda: struct.unpack(">b", self._read_exact(1))[0],
            b"I": lambda: struct.unpack(">h", self._read_exact(2))[0],
            b"l": lambda: struct.unpack(">i", self._read_exact(4))[0],
            b"L": lambda: struct.unpack(">q", self._read_exact(8))[0],
        }.get(type_marker)

        if length is None:
            raise UBJSONDecodeError(f"Invalid length type: {type_marker}")

        value = length()
        if value < 0:
            raise UBJSONDecodeError(f"Negative length not allowed: {value}")
        return value

    def _parse_type(self) -> _JTYPE:
        value_type = None
        count = None

        marker = self.fp.read(1)
        match marker:
            case b'[' | b'{':
                # grab dollar sign ?
                if b'$' == dollar_sign := self.fp.read(1):
                    ## recurse _parse_type
                    value_type = self._parse_type()
                #else: ##f edge case - array no type == deepest collection has no type
                # grab pound sign ?
                if b'#' == pound_sign := self.fp.read(1):
                    ## call _decode_length
                    count = self._decode_length()
                else:
                    ##f edge case - deepest type (could be outer type) is collection with no length (and no type) -- pound sign fails
                    self.fp.seek(-1, SEEK_CUR)
                    f = lambda x: None if x[0] is None else ((x[0][0], f(x[0][1])), x[0][1][1])
                    try:
                        return f((marker, (value_type, None)))
                    except:
                        # TypeError or IndexError when input is formatted wrong
                        raise UBJSONDecodeError(f"Typed collection without count, expected b'#' got: {pound_sign}")
                # return type
                return (marker, (value_type, count))
            case _:
                # non-collection types are defined by one character
                return marker

    def _decode_array(self, array_type:Union[None, tuple[_JTYPE, int]]) -> list:
        items = []

        match array_type:
            case None:
                # Sentinel-based parsing
                while True:
                    peek = self.fp.read(1)
                    if not peek:
                        raise UBJSONDecodeError("Unexpected end of array.")
                    if peek == b"]":
                        break
                    self.fp.seek(-1, SEEK_CUR)
                    items.append(self._decode_from_type(None))
            case (jtype, count):
                # check if array is of fixed-length type
                ctype, bytesize = {
                    b'i': ('b', 1),
                    b'U': ('B', 1),
                    b'I': ('h', 2),
                    b'l': ('l', 4),
                    b'L': ('q', 8),
                    b'd': ('f', 4),
                    b'D': ('d', 8),
                }.get(value_type, (None, None))

                if ctype is not None:
                    items = array(ctype, self._read_exact(bytesize*count)).tolist()
                else:
                    # array body is not known length in bytes
                    for _ in range(count):
                        items.append(self._decode_from_type(jtype))

        return items

    def _decode_object(self, object_type:Union[None, tuple[_JTYPE, int]]) -> dict:
        obj = {}

        match object_type:
            case None:
                while True:
                    peek = self.fp.read(1)
                    if not peek:
                        raise UBJSONDecodeError("Unexpected end of object.")
                    if peek == b"}":
                        break
                    self.fp.seek(-1, 1)
                    key = self._decode_string()
                    value = self._decode_from_type(None)
                    obj[key] = value
            case (jtype, count):
                for _ in range(count):
                    key = self._decode_string()
                    value = self._decode_from_type(jtype)
                    obj[key] = value

        return obj

