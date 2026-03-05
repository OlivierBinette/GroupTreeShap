import struct
from io import BytesIO, SEEK_CUR
from typing import Union, BinaryIO, Optional
from array import array
import json

SPECIAL_TYPES = frozenset({
    b'Z',
    b'N',
    b'T',
    b'F',
})
NUMERIC_TYPES = frozenset({
    b'i',
    b'U',
    b'I',
    b'l',
    b'L',
    b'd',
    b'D',
    b'H',
})
CONTAINER_TYPES = frozenset({
    b'[',
    b'{'
})

# Mapping of some numeric UBJSON types to C types and their byte size.
OPTIMIZED_TYPECODES = {
    b'i': ('b', 1),
    b'U': ('B', 1),
    b'I': ('h', 2),
    b'l': ('l', 4),
    b'L': ('q', 8),
    b'd': ('f', 4),
    b'D': ('d', 8),
}

class UBJSONDecodeError(Exception):
    pass

class UBJSONUnsupportedError(Exception):
    pass

class UBJSONDecoder:
    def __init__(self, ubj):
        self.ubj = ubj

    def decode(self):
        return decode(self.ubj)

def decode(ubj: bytes | bytearray | BytesIO):
    if not isinstance(ubj, BytesIO):
        ubj = BytesIO(ubj)

    marker = get_next_marker(ubj)
    result = read_element(ubj, marker)
    
    while (end_marker := ubj.read(1)) == b'N':
        continue
    if end_marker != b'':
        raise UBJSONDecodeError()
    else:
        return result

def read_element(ubj: BytesIO, marker):
    if marker in NUMERIC_TYPES:
        return read_numeric(ubj, marker)
    elif marker in SPECIAL_TYPES:
        return read_special(marker)
    elif marker in CONTAINER_TYPES:
        return read_container(ubj, marker)
    elif marker == b'S':
        return read_string(ubj, marker)
    elif marker == b'C':
        return read_char(ubj, marker)
    else:
        raise UBJSONDecodeError()


def get_next_marker(ubj: BytesIO):
    while (marker := ubj.read(1)) == b'N':
        continue

    return marker

def read_char(ubj: BytesIO, marker):
    match marker:
        case b'C':
            return ubj.read(1).decode("utf-8")
        case _:
            raise UBJSONDecodeError()
        
def read_string(ubj: BytesIO, marker):
    match marker:
        case b'S':
            length = read_numeric(ubj, get_next_marker(ubj))
            return ubj.read(length).decode("utf-8")
        case _:
            raise UBJSONDecodeError()

def read_numeric(ubj: BytesIO, marker):
    match marker:
        case b'i': # int8
            return struct.unpack('b', ubj.read(1))[0]
        case b'U': # uint8
            return struct.unpack('B', ubj.read(1))[0]
        case b'I': # int16
            return struct.unpack('>h', ubj.read(2))[0]
        case b'l': # int32
            return struct.unpack('>i', ubj.read(4))[0]
        case b'L': # int64
            return struct.unpack('>q', ubj.read(8))[0]
        case b'd': # float32
            return struct.unpack('f', ubj.read(4))[0]
        case b'D': # float64
            return struct.unpack('d', ubj.read(8))[0]
        case b'H': # High precision
            return json.loads(read_string(ubj))
        case _:
            raise UBJSONDecodeError()

def read_special(marker):
    match marker:
        case b'Z':
            return None
        case b'T':
            return True
        case b'F':
            return False
        case _:
            raise UBJSONDecodeError()

def get_container_type(ubj: BytesIO):
    type_markers = []
    fully_typed = False
    while get_next_marker(ubj) == b'$':
        marker = get_next_marker(ubj)
        type_markers += [marker]
        if marker not in [b'[', b'{']:
            fully_typed = True
            break

    counts = []
    if fully_typed:
        for _ in range(len(type_markers)):
            if get_next_marker(ubj) != b'#':
                raise UBJSONDecodeError()
            marker = get_next_marker(ubj)
            counts.insert(0, read_numeric(ubj, marker))
        if len(type_markers) != len(counts):
            raise UBJSONDecodeError()
    else:
        ubj.seek(-1, SEEK_CUR)
        while get_next_marker(ubj) == b'#':
            marker = get_next_marker(ubj)
            counts.insert(0, read_numeric(ubj, marker))
        ubj.seek(-1, SEEK_CUR)

        if len(type_markers) - len(counts) < -1:
            raise UBJSONDecodeError()

    return (type_markers, counts)

def read_container(ubj: BytesIO, marker, type_spec = None):    
    if marker == b'[':
        return read_list(ubj, type_spec)
    elif marker == b'{':
        return read_dict(ubj, type_spec)

def read_dict(ubj: BytesIO, type_spec = None):
    if type_spec is None:
        (type_markers, counts) = get_container_type(ubj)
    else: 
        (type_markers, counts) = type_spec

    container = dict()
    endmark = b'}'

    if len(type_markers) == 0 and len(counts) == 0:
        while (marker := get_next_marker(ubj)) != endmark:
            ubj.seek(-1, SEEK_CUR)
            key = read_string(ubj, b'S')
            container[key] = read_element(ubj, get_next_marker(ubj))
        return container
    elif len(type_markers) == 0 and len(counts) == 1:
        for _ in range(counts[0]):
            key = read_string(ubj, b'S')
            container[key] = read_element(ubj, get_next_marker(ubj))
        return container
    elif len(type_markers) >= 1:
        if type_markers[0] in [b'[', b'{']:
            type_spec = (type_markers[1:], counts[1:])
            for _ in range(counts[0]):
                if len(counts) == 1:
                    type_spec = get_container_type(ubj)
                key = read_string(ubj, b'S')
                container[key] = read_container(ubj, type_markers[0], type_spec)
            return container
        elif type_markers[0] in SPECIAL_TYPES:
            for _ in range(counts[0]):
                key = read_string(ubj, b'S')
                container[key] = read_special(type_markers[0])
            return container
        elif type_markers[0] in NUMERIC_TYPES:
            for _ in range(counts[0]):
                key = read_string(ubj, b'S')
                container[key] = read_numeric(ubj, type_markers[0])
            return container
        else:
            for _ in range(counts[0]):
                key = read_string(ubj, b'S')
                container[key] = read_element(ubj, type_markers[0])
            return container

def read_list(ubj: BytesIO, type_spec = None):
    if type_spec is None:
        (type_markers, counts) = get_container_type(ubj)
    else: 
        (type_markers, counts) = type_spec

    container = list()

    if len(type_markers) == 0 and len(counts) == 0:
        while (marker := get_next_marker(ubj)) != b']':
            container.append(read_element(ubj, marker))
        return container
    elif len(type_markers) == 0 and len(counts) == 1:
        for _ in range(counts[0]):
            marker = get_next_marker(ubj)
            container.append(read_element(ubj, marker))
        return container
    elif len(type_markers) >= 1:
        if type_markers[0] in [b'[', b'{']:
            type_spec = (type_markers[1:], counts[1:])
            for _ in range(counts[0]):
                if len(counts) <= 1:
                    type_spec = get_container_type(ubj)
                container.append(read_container(ubj, type_markers[0], type_spec))
            return container
        elif type_markers[0] in SPECIAL_TYPES:
            return [read_special(type_markers[0])]*counts[0]
        elif type_markers[0] in NUMERIC_TYPES :
            if type_markers[0] in OPTIMIZED_TYPECODES:
                ctype, bytesize = OPTIMIZED_TYPECODES[type_markers[0]]
                return array(ctype, ubj.read(counts[0]*bytesize)).tolist()
            else:
                for _ in range(counts[0]):
                    container.append(read_numeric(ubj, type_markers[0]))
                return container
        else:
            return [read_element(ubj, type_markers[0])] * counts[0]