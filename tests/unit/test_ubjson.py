import pytest

from grouptreeshap.ubjson import UBJSONDecoder

ubjson_examples = [
    # Null
    (b'Z', None),
    (b'NZNN', None),  # parser should ignore N (no-op)

    # Booleans
    (b'T', True),
    (b'F', False),

    # int8
    (b'i\x2a', 42),
    (b'i\xfb', -5),

    # uint8
    (b'U\xc8', 200),

    # int16
    (b'I\x03\xe8', 1000),
    (b'I\xfc\x18', -1000),

    # int32
    (b'l\x00\x01\x86\xa0', 100000),

    # int64
    (b'L\x00\x00\x00\x00\x00\x01\x86\xa0', 100000),

    # float32
    (b'd\x3f\xc0\x00\x00', 1.5),

    # float64
    (b'D\x3f\xf8\x00\x00\x00\x00\x00\x00', 1.5),

    # char
    (b'Ca', "a"),

    # string
    (b'Si\x00', ""),
    (b'Si\x01a', "a"),
    (b'Si\x06UBJSON', "UBJSON"),
    (b'Sl\x00\x00\x00\x01a', "a"),
    (b'Si\x02\xc3\xa9', "é"),  # "é" is 2 bytes in UTF-8


    # ------
    # Arrays
    # ------

    # Unoptimized mixed array: [null, true, "hi", 42]
    # [ [Z] [T] [S][i][2][hi] [i][42] ]
    (b'[ZTSi\x02hii\x2a]', [None, True, "hi", 42]),

    # Unoptimized nested array: [[1,2],[3]]
    # [ [ [i][1] [i][2] ] [ [i][3] ] ]
    (
        b'['
          b'[i\x01i\x02]'
          b'[i\x03]'
        b']',
        [[1, 2], [3]]
    ),

    # Optimized with count only: [1,2,3] as 3 elements (no closing ']')
    # [ [#][i][3]  [i][1] [i][2] [i][3] ]
    (b'[#i\x03i\x01i\x02i\x03', [1, 2, 3]),

    # Optimized with type + count: float32 array
    # [ [$][d][#][i][3]  [1.0] [2.0] [1.5]
    (
        b'[$d#i\x03'
        b'\x3f\x80\x00\x00'
        b'\x40\x00\x00\x00'
        b'\x3f\xc0\x00\x00',
        [1.0, 2.0, 1.5]
    ),

    # Strongly typed nested arrays
    (
        b'[$[#i\x02'
            b'[$i#i\x02\x01\x02'
            b'[$i#i\x02\x03\x04',
        [[1, 2], [3, 4]]
    ),

    # Strongly typed nested arrays - fully optimized
    (
        b'[$[$i#i\x02#i\x02'
            b'\x01\x02'
            b'\x03\x04',
        [[1, 2], [3, 4]]
    ),

    # Special cases with empty body optimization:

    # 3 None: [ [$][Z][#][i][3] ]
    (b'[$Z#i\x03', [None, None, None]),

    # 5 True: [ [$][T][#][i][5] ]
    (b'[$T#i\x05', [True]*5),
    
    # 5 False: [ [$][T][#][i][5] ]
    (b'[$F#i\x05', [False]*5),
]

@pytest.mark.parametrize("ubj,expected", ubjson_examples)
def test_decode_examples(ubj, expected):
    assert UBJSONDecoder(ubj).decode() == expected

    # Test decode is as expected when no-ops are added
    assert UBJSONDecoder(b'N' + ubj + b'N').decode() == expected

    # Test decode is as expected when part of a list
    inlist = b'[i\x01' + ubj + b'i\x02]'
    assert UBJSONDecoder(inlist).decode() == [1, expected, 2]

    # Test decode is as expected when part of a dict
    indict = b'{i\x07content' + ubj + b'i\x05afterZ}'
    assert UBJSONDecoder(indict).decode() == {"content": expected, "after": None}