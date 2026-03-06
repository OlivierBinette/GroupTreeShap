import pytest
import struct

from grouptreeshap.ubjson import UBJSONDecoder, UBJSONDecodeError
from tests.resources.ubj_examples import UBJSON_EXAMPLES, INVALID_EXAMPLES
from io import BytesIO

def ubj_key(key: str) -> bytes:
    data = key.encode("utf-8")
    return b"U" + bytes([len(data)]) + data

@pytest.mark.parametrize("ubj,expected", UBJSON_EXAMPLES)
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

def test_noop_array_type_unsupported():
    with pytest.raises(UBJSONDecodeError):
        UBJSONDecoder(b'[$N#i\x00').decode()  # Array of length 0 of type no-op.
    with pytest.raises(UBJSONDecodeError):
        UBJSONDecoder(b'[$N#i\x03').decode()  # Array of length 3 of type no-op.

def test_noop_object_type_unsupported():
    with pytest.raises(UBJSONDecodeError):
        UBJSONDecoder(b'{$N#i\x00').decode()  # Empty object of type no-op.

    with pytest.raises(UBJSONDecodeError):
        UBJSONDecoder(b'{$N#i\x02i\x05noop1i\x05noop2').decode()  # Object of size 2 of type no-op.

@pytest.mark.parametrize("ubj", INVALID_EXAMPLES)
def test_raise_on_invalid(ubj):
    print(ubj)
    with pytest.raises(UBJSONDecodeError):
        UBJSONDecoder(ubj).decode()

def test_get_container_typespec():
    from grouptreeshap.ubjson.decoder import get_container_typespec

    assert get_container_typespec(BytesIO(b'i\x00')) == ([], [])
    assert get_container_typespec(BytesIO(b'$[#i\x01')) == ([b'['], [1])
    assert get_container_typespec(BytesIO(b'#i\x01')) == ([], [1])

def test_get_next_marker_skips_noops():
    from grouptreeshap.ubjson.decoder import get_next_marker

    ubj = BytesIO(b"NNT")
    assert get_next_marker(ubj) == b"T"


def test_read_char_reads_one_utf8_char():
    from grouptreeshap.ubjson.decoder import read_char

    assert read_char(BytesIO(b"A")) == "A"

def test_read_string_reads_length_prefixed_utf8():
    from grouptreeshap.ubjson.decoder import read_string

    assert read_string(BytesIO(b"U\x03hey")) == "hey"

@pytest.mark.parametrize(
    ("marker, payload, expected"),
    [
        (b"i", b"\xff", -1),
        (b"U", b"\x07", 7),
        (b"I", struct.pack(">h", -123), -123),
        (b"l", struct.pack(">i", 123456), 123456),
        (b"L", struct.pack(">q", -123456789), -123456789),
    ],
)
def test_read_numeric_integers(marker, payload, expected):
    from grouptreeshap.ubjson.decoder import read_numeric

    assert read_numeric(BytesIO(payload), marker) == expected

def test_read_numeric_float():
    from grouptreeshap.ubjson.decoder import read_numeric

    result = read_numeric(BytesIO(struct.pack(">f", 1.25)), b"d")
    assert result == 1.25

    result = read_numeric(BytesIO(struct.pack(">d", 1.25)), b"D")
    assert result == 1.25

def test_read_numeric_invalid_marker_raises():
    from grouptreeshap.ubjson.decoder import read_numeric

    with pytest.raises(UBJSONDecodeError):
        read_numeric(BytesIO(b""), b"X")

@pytest.mark.parametrize(
    ("marker, expected"),
    [
        (b"Z", None),
        (b"T", True),
        (b"F", False),
    ],
)
def test_read_special_values(marker, expected):
    from grouptreeshap.ubjson.decoder import read_special

    assert read_special(marker) is expected

def test_read_special_invalid():
    from grouptreeshap.ubjson.decoder import read_special

    with pytest.raises(UBJSONDecodeError):
        read_special(b"N")
    with pytest.raises(UBJSONDecodeError):
        read_special(b"X")

def test_get_container_types_markers_reads_nested_markers():
    from grouptreeshap.ubjson.decoder import get_container_types_markers

    ubj = BytesIO(b"$[$U")
    assert get_container_types_markers(ubj) == [b"[", b"U"]

def test_get_container_counts_reads_required_counts():
    from grouptreeshap.ubjson.decoder import get_container_counts

    ubj = BytesIO(b"#i\x03")
    assert get_container_counts(ubj, [b"U"]) == [3]

def test_read_list_unoptimized_without_count_reads_until_end():
    from grouptreeshap.ubjson.decoder import read_list_unoptimized

    ubj = BytesIO(b"U\x01T]")
    assert read_list_unoptimized(ubj, None) == [1, True]

def test_read_list_unoptimized_with_count_reads_fixed_items():
    from grouptreeshap.ubjson.decoder import read_list_unoptimized

    ubj = BytesIO(b"U\x01T")
    assert read_list_unoptimized(ubj, 2) == [1, True]

def test_read_list_optimized_special_values():
    from grouptreeshap.ubjson.decoder import read_list_optimized

    assert read_list_optimized(BytesIO(b""), [b"T"], [3]) == [True, True, True]

def test_read_list_optimized_numeric_values():
    from grouptreeshap.ubjson.decoder import read_list_optimized
    
    ubj = BytesIO(b"\x01\x02\x03")
    assert read_list_optimized(ubj, [b"U"], [3]) == [1, 2, 3]

def test_read_dict_unoptimized_without_count_reads_until_end():
    from grouptreeshap.ubjson.decoder import read_dict_unoptimized

    ubj = BytesIO(
        ubj_key("a") + b"U\x01" +
        ubj_key("b") + b"T" +
        b"}"
    )
    assert read_dict_unoptimized(ubj, None) == {"a": 1, "b": True}

def test_read_dict_unoptimized_with_count_reads_fixed_items():
    from grouptreeshap.ubjson.decoder import read_dict_unoptimized

    ubj = BytesIO(
        ubj_key("a") + b"U\x01" +
        ubj_key("b") + b"T"
    )
    assert read_dict_unoptimized(ubj, 2) == {"a": 1, "b": True}

def test_read_dict_optimized_reads_typed_values():
    from grouptreeshap.ubjson.decoder import read_dict_optimized

    ubj = BytesIO(ubj_key("a") + ubj_key("b"))
    assert read_dict_optimized(ubj, [b"T"], [2]) == {"a": True, "b": True}