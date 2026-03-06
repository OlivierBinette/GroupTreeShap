import struct
from io import BytesIO, SEEK_CUR
from array import array
import json
import sys

from grouptreeshap.ubjson.markers import (
    CONTAINER_TYPES,
    NUMERIC_TYPES,
    SPECIAL_TYPES,
    OPTIMIZED_TYPECODES,
)

JSONLike = None | bool | int | float | str | list["JSONLike"] | dict[str, "JSONLike"]


class UBJSONDecodeError(Exception):
    pass


class UBJSONUnsupportedError(UBJSONDecodeError):
    pass


class UBJSONDecoder:
    def __init__(self, ubj):
        if not isinstance(ubj, BytesIO):
            self.ubj = BytesIO(ubj)
        else:
            self.ubj = ubj

    def decode(self) -> JSONLike:
        return decode(self.ubj)


def decode(ubj: BytesIO) -> JSONLike:
    marker = get_next_marker(ubj)
    result = read_element(ubj, marker)

    while (end_marker := ubj.read(1)) == b"N":
        continue
    if end_marker != b"":
        raise UBJSONDecodeError(f"Unexpected continuation at position {ubj.tell()}")
    else:
        return result


def read_bytes(ubj: BytesIO, length: int) -> bytes:
    content = ubj.read(length)
    if len(content) != length:
        raise UBJSONDecodeError(f"Unexpected end of stream at position {ubj.tell()}.")

    return content


def read_element(
    ubj: BytesIO, marker: bytes, type_spec: tuple | None = None
) -> JSONLike:
    if marker in NUMERIC_TYPES:
        return read_numeric(ubj, marker)
    elif marker in SPECIAL_TYPES:
        return read_special(marker)
    elif marker in CONTAINER_TYPES:
        return read_container(ubj, marker, type_spec)
    elif marker == b"S":
        return read_string(ubj)
    elif marker == b"C":
        return read_char(ubj)
    else:
        raise UBJSONDecodeError(
            f"Invalid marker {marker} encountered at position {ubj.tell()}"
        )


def get_next_marker(ubj: BytesIO) -> bytes:
    while (marker := ubj.read(1)) == b"N":
        continue

    return marker


def read_char(ubj: BytesIO) -> str:
    return read_bytes(ubj, 1).decode("utf-8")


def read_string(ubj: BytesIO) -> str:
    length = read_numeric(ubj, get_next_marker(ubj))
    return read_bytes(ubj, length).decode("utf-8")


def read_numeric(ubj: BytesIO, marker: bytes) -> int | float:
    match marker:
        case b"i":  # int8
            return struct.unpack("b", read_bytes(ubj, 1))[0]
        case b"U":  # uint8
            return struct.unpack("B", read_bytes(ubj, 1))[0]
        case b"I":  # int16
            return struct.unpack(">h", read_bytes(ubj, 2))[0]
        case b"l":  # int32
            return struct.unpack(">i", read_bytes(ubj, 4))[0]
        case b"L":  # int64
            return struct.unpack(">q", read_bytes(ubj, 8))[0]
        case b"d":  # float32
            return struct.unpack(">f", read_bytes(ubj, 4))[0]
        case b"D":  # float64
            return struct.unpack(">d", read_bytes(ubj, 8))[0]
        case b"H":  # High precision
            return json.loads(read_string(ubj))
        case _:
            raise UBJSONDecodeError(
                f"Invalid numeric marker {marker} encountered at position {ubj.tell()}"
            )


def read_special(marker: bytes) -> None | bool:
    match marker:
        case b"Z":
            return None
        case b"T":
            return True
        case b"F":
            return False
        case b"N":
            raise UBJSONUnsupportedError(f"Marker N is not a supported value.")
        case _:
            raise UBJSONDecodeError(f"Invalid special marker {marker} encountered.")


def read_container(
    ubj: BytesIO, marker: bytes, type_spec: None | tuple
) -> list[JSONLike] | dict[str, JSONLike]:
    if type_spec is None or type_spec == ([], []):
        type_markers, counts = get_container_typespec(ubj)
    else:
        type_markers, counts = type_spec

    if marker == b"[":
        return read_list(ubj, type_markers, counts)
    elif marker == b"{":
        return read_dict(ubj, type_markers, counts)
    else:
        raise UBJSONDecodeError(
            f"Invalid container marker {marker} at position {ubj.tell()}"
        )


def get_container_types_markers(ubj: BytesIO) -> list[bytes]:
    type_markers = []
    while get_next_marker(ubj) == b"$":
        marker = get_next_marker(ubj)
        type_markers += [marker]
        if marker not in [b"[", b"{"]:
            break
    else:
        ubj.seek(-1, SEEK_CUR)

    return type_markers


def get_container_counts(ubj, type_markers) -> list[int]:
    counts = []
    for _ in range(len(type_markers)):
        marker = get_next_marker(ubj)
        if marker != b"#":
            raise UBJSONDecodeError(f"Expected count marker # at position {ubj.tell()}")
        counts.insert(0, read_numeric(ubj, get_next_marker(ubj)))

    if len(type_markers) == 0 or type_markers[-1] in [b"[", b"{"]:
        marker = get_next_marker(ubj)
        if marker == b"#":
            counts.insert(0, read_numeric(ubj, get_next_marker(ubj)))
        else:
            ubj.seek(-1, SEEK_CUR)

    return counts


def get_container_typespec(ubj: BytesIO) -> tuple:
    type_markers = get_container_types_markers(ubj)
    counts = get_container_counts(ubj, type_markers)

    return type_markers, counts


def read_list_unoptimized(
    ubj: BytesIO, count: int | None, type_spec: None | tuple = None
) -> list[JSONLike]:
    container = list()
    if count is None:
        while (marker := get_next_marker(ubj)) != b"]":
            container.append(read_element(ubj, marker, type_spec))
        return container
    else:
        for _ in range(count):
            marker = get_next_marker(ubj)
            container.append(read_element(ubj, marker, type_spec))
        return container


def read_list_optimized(
    ubj: BytesIO, type_markers: list[bytes], counts: list[int]
) -> list[JSONLike]:
    container = list()

    if type_markers[0] in SPECIAL_TYPES:
        return [read_special(type_markers[0])] * counts[0]
    elif type_markers[0] in OPTIMIZED_TYPECODES:
        ctype, bytesize = OPTIMIZED_TYPECODES[type_markers[0]]
        arr = array(ctype, read_bytes(ubj, counts[0] * bytesize))
        if sys.byteorder == "little":
            arr.byteswap()
        return arr.tolist()
    else:
        for _ in range(counts[0]):
            container.append(
                read_element(ubj, type_markers[0], (type_markers[1:], counts[1:]))
            )
        return container


def read_list(
    ubj: BytesIO, type_markers: list[bytes], counts: list[int]
) -> list[JSONLike]:
    if len(type_markers) == 0:
        count = counts[0] if len(counts) > 0 else None
        return read_list_unoptimized(ubj, count, (type_markers[1:], counts[1:]))
    else:
        return read_list_optimized(ubj, type_markers, counts)


def read_dict_unoptimized(
    ubj: BytesIO, count: int | None, type_spec: None | tuple = None
) -> dict[str, JSONLike]:
    container = dict()
    if count is None:
        while (marker := get_next_marker(ubj)) != b"}":
            ubj.seek(-1, SEEK_CUR)
            key = read_string(ubj)
            marker = get_next_marker(ubj)
            container[key] = read_element(ubj, marker, type_spec)
        return container
    else:
        for _ in range(count):
            key = read_string(ubj)
            marker = get_next_marker(ubj)
            container[key] = read_element(ubj, marker, type_spec)
        return container


def read_dict_optimized(
    ubj: BytesIO, type_markers: list[bytes], counts: list[int]
) -> dict[str, JSONLike]:
    container = dict()
    for _ in range(counts[0]):
        key = read_string(ubj)
        container[key] = read_element(
            ubj, type_markers[0], (type_markers[1:], counts[1:])
        )
    return container


def read_dict(
    ubj: BytesIO, type_markers: list[bytes], counts: list[int]
) -> dict[str, JSONLike]:
    if len(type_markers) == 0:
        count = counts[0] if len(counts) > 0 else None
        return read_dict_unoptimized(ubj, count, (type_markers[1:], counts[1:]))
    else:
        return read_dict_optimized(ubj, type_markers, counts)
