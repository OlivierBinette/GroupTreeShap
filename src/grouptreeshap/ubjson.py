import struct
from io import BytesIO
from typing import Union, BinaryIO, Optional


class UBJSONDecodeError(Exception):
    pass


class UBJSONDecoder:
    def __init__(self, byte_stream: Union[bytes, BinaryIO]):
        if isinstance(byte_stream, (bytes, bytearray)):
            byte_stream = BytesIO(byte_stream)
        elif not hasattr(byte_stream, "read"):
            raise TypeError("Expected bytes, bytearray, or a binary file-like object")
        self.fp: BinaryIO = byte_stream

    def decode(self) -> object:
        return self._decode_value()

    def _read_exact(self, n: int) -> bytes:
        data = self.fp.read(n)
        if len(data) != n:
            raise UBJSONDecodeError(
                f"Unexpected end of stream. Expected {n} bytes, got {len(data)}."
            )
        return data

    def _decode_value(self) -> object:
        while True:
            marker = self.fp.read(1)
            if not marker:
                raise UBJSONDecodeError("Unexpected end of stream.")
            marker = marker.decode("ascii")
            if marker != "N":  # Skip no-op
                return self._decode_by_marker(marker)

    def _decode_by_marker(self, marker: str) -> object:
        if marker == "Z":
            return None
        elif marker == "T":
            return True
        elif marker == "F":
            return False
        elif marker == "i":
            return struct.unpack(">b", self._read_exact(1))[0]
        elif marker == "U":
            return struct.unpack(">B", self._read_exact(1))[0]
        elif marker == "I":
            return struct.unpack(">h", self._read_exact(2))[0]
        elif marker == "l":
            return struct.unpack(">i", self._read_exact(4))[0]
        elif marker == "L":
            return struct.unpack(">q", self._read_exact(8))[0]
        elif marker == "d":
            return struct.unpack(">f", self._read_exact(4))[0]
        elif marker == "C":
            return self._read_exact(1).decode("utf-8")
        elif marker == "S":
            return self._decode_string()
        elif marker == "[":
            return self._decode_array()
        elif marker == "{":
            return self._decode_object()
        else:
            raise UBJSONDecodeError(f"Unknown marker: {marker}")

    def _decode_string(self) -> str:
        length = self._decode_length()
        return self._read_exact(length).decode("utf-8")

    def _decode_length(self) -> int:
        type_marker = self.fp.read(1).decode("ascii")

        length = {
            "U": lambda: struct.unpack(">B", self._read_exact(1))[0],
            "i": lambda: struct.unpack(">b", self._read_exact(1))[0],
            "I": lambda: struct.unpack(">h", self._read_exact(2))[0],
            "l": lambda: struct.unpack(">i", self._read_exact(4))[0],
            "L": lambda: struct.unpack(">q", self._read_exact(8))[0],
        }.get(type_marker)

        if length is None:
            raise UBJSONDecodeError(f"Invalid length type: {type_marker}")

        value = length()
        if value < 0:
            raise UBJSONDecodeError(f"Negative length not allowed: {value}")
        return value

    def _parse_type_and_count_headers(self) -> tuple[Optional[str], Optional[int]]:
        value_type = None
        count = None

        while True:
            marker = self.fp.read(1)
            if marker == b"$":
                value_type = self.fp.read(1).decode("ascii")
            elif marker == b"#":
                count = self._decode_length()
            else:
                self.fp.seek(-1, 1)
                break

        return value_type, count

    def _decode_array(self) -> list:
        value_type, count = self._parse_type_and_count_headers()

        items = []
        if count is not None:
            for _ in range(count):
                if value_type:
                    items.append(self._decode_by_marker(value_type))
                else:
                    items.append(self._decode_value())
        else:
            # Sentinel-based parsing
            while True:
                peek = self.fp.read(1)
                if not peek:
                    raise UBJSONDecodeError("Unexpected end of array.")
                if peek == b"]":
                    break
                self.fp.seek(-1, 1)
                items.append(self._decode_value())
        return items

    def _decode_object(self) -> dict:
        value_type, count = self._parse_type_and_count_headers()

        obj = {}
        if count is not None:
            for _ in range(count):
                key = self._decode_string()
                if value_type:
                    value = self._decode_by_marker(value_type)
                else:
                    value = self._decode_value()
                obj[key] = value
        else:
            while True:
                peek = self.fp.read(1)
                if not peek:
                    raise UBJSONDecodeError("Unexpected end of object.")
                if peek == b"}":
                    break
                self.fp.seek(-1, 1)
                key = self._decode_string()
                value = self._decode_value()
                obj[key] = value
        return obj
