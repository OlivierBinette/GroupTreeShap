SPECIAL_TYPES = frozenset(
    {
        b"Z",
        b"N",
        b"T",
        b"F",
    }
)
NUMERIC_TYPES = frozenset(
    {
        b"i",
        b"U",
        b"I",
        b"l",
        b"L",
        b"d",
        b"D",
        b"H",
    }
)
CONTAINER_TYPES = frozenset({b"[", b"{"})

# Mapping of some numeric UBJSON types to C types and their byte size.
OPTIMIZED_TYPECODES = {
    b"i": ("b", 1),
    b"U": ("B", 1),
    b"I": ("h", 2),
    b"l": ("i", 4),
    b"L": ("l", 8),
    b"d": ("f", 4),
    b"D": ("d", 8),
}
