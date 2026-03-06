# Tree with two interacting features (x1 and x2), and an additively independent feature (x3)
#
# For a binary data, this is equal to x1 * x2 + 10 * x3
#
# if x3 <= 0.5:
#     if x1 <= 0.5:
#         if x2 <= 0.5: return 0
#         else:         return 0
#     else:
#         if x2 <= 0.5: return 0
#         else:         return 1
# else:
#     if x1 <= 0.5:
#         if x2 <= 0.5: return 10
#         else:         return 10
#     else:
#         if x2 <= 0.5: return 10
#         else:         return 11
TREE_TWO_DEP_ONE_INDEP = dict(
    feature=[
        2,  # 0: x3
        0,  # 1: x1
        1,  # 2: x2
        0,  # 3: leaf
        0,  # 4: leaf
        1,  # 5: x2
        0,  # 6: leaf
        0,  # 7: leaf
        0,  # 8: x1
        1,  # 9: x2
        0,  # 10: leaf
        0,  # 11: leaf
        1,  # 12: x2
        0,  # 13: leaf
        0,  # 14: leaf
    ],
    children_left=[
        1,  # 0
        2,  # 1
        3,  # 2
        -1,  # 3
        -1,  # 4
        6,  # 5
        -1,  # 6
        -1,  # 7
        9,  # 8
        10,  # 9
        -1,  # 10
        -1,  # 11
        13,  # 12
        -1,  # 13
        -1,  # 14
    ],
    children_right=[
        8,  # 0
        5,  # 1
        4,  # 2
        -1,  # 3
        -1,  # 4
        7,  # 5
        -1,  # 6
        -1,  # 7
        12,  # 8
        11,  # 9
        -1,  # 10
        -1,  # 11
        14,  # 12
        -1,  # 13
        -1,  # 14
    ],
    missing_go_to_left=[True] * 15,
    threshold=[
        0.5,  # 0: x3 <= 0.5
        0.5,  # 1: x1 <= 0.5
        0.5,  # 2: x2 <= 0.5
        -1.0,  # 3: leaf
        -1.0,  # 4: leaf
        0.5,  # 5: x2 <= 0.5
        -1.0,  # 6: leaf
        -1.0,  # 7: leaf
        0.5,  # 8: x1 <= 0.5
        0.5,  # 9: x2 <= 0.5
        -1.0,  # 10: leaf
        -1.0,  # 11: leaf
        0.5,  # 12: x2 <= 0.5
        -1.0,  # 13: leaf
        -1.0,  # 14: leaf
    ],
    value=[
        0.0,  # 0 internal
        0.0,  # 1
        0.0,  # 2
        0.0,  # 3 leaf
        0.0,  # 4 leaf
        0.0,  # 5
        0.0,  # 6 leaf
        1.0,  # 7 leaf
        0.0,  # 8
        0.0,  # 9
        10.0,  # 10 leaf
        10.0,  # 11 leaf
        0.0,  # 12
        10.0,  # 13 leaf
        11.0,  # 14 leaf
    ],
    weighted_n_node_samples=[
        8.0,  # 0
        4.0,  # 1
        2.0,  # 2
        1.0,  # 3
        1.0,  # 4
        2.0,  # 5
        1.0,  # 6
        1.0,  # 7
        4.0,  # 8
        2.0,  # 9
        1.0,  # 10
        1.0,  # 11
        2.0,  # 12
        1.0,  # 13
        1.0,  # 14
    ],
    split_type=[0] * 15,  # Only numeric splits
    categories_nodes=[],
    categories=[],
    categories_segments=[],
    categories_sizes=[],
)

# Tree with three interacting features features and one additively independent feature
#
# For binary data, this is equal to x0 * x1 * x2 + 10 * x3
#
# if x3 <= 0.5:
#     if x0 <= 0.5:
#         return 0
#     else:
#         if x1 <= 0.5:
#             return 0
#         else:
#             if x2 <= 0.5: return 0
#             else:         return 1
# else:
#     if x0 <= 0.5:
#         return 10
#     else:
#         if x1 <= 0.5:
#             return 10
#         else:
#             if x2 <= 0.5: return 10
#             else:         return 11
TREE_THREE_DEP_ONE_INDEP = dict(
    feature=[
        3,  # 0: x3
        0,  # 1: x0
        -2,  # 2: leaf
        1,  # 3: x1
        -2,  # 4: leaf
        2,  # 5: x2
        -2,  # 6: leaf
        -2,  # 7: leaf
        0,  # 8: x0
        -2,  # 9: leaf
        1,  # 10: x1
        -2,  # 11: leaf
        2,  # 12: x2
        -2,  # 13: leaf
        -2,  # 14: leaf
    ],
    children_left=[
        1,  # 0
        2,  # 1
        -1,  # 2
        4,  # 3
        -1,  # 4
        6,  # 5
        -1,  # 6
        -1,  # 7
        9,  # 8
        -1,  # 9
        11,  # 10
        -1,  # 11
        13,  # 12
        -1,  # 13
        -1,  # 14
    ],
    children_right=[
        8,  # 0
        3,  # 1
        -1,  # 2
        5,  # 3
        -1,  # 4
        7,  # 5
        -1,  # 6
        -1,  # 7
        10,  # 8
        -1,  # 9
        12,  # 10
        -1,  # 11
        14,  # 12
        -1,  # 13
        -1,  # 14
    ],
    missing_go_to_left=[True] * 15,
    threshold=[
        0.5,  # 0: x3 <= 0.5
        0.5,  # 1: x0 <= 0.5
        -1.0,  # 2: leaf
        0.5,  # 3: x1 <= 0.5
        -1.0,  # 4: leaf
        0.5,  # 5: x2 <= 0.5
        -1.0,  # 6: leaf
        -1.0,  # 7: leaf
        0.5,  # 8: x0 <= 0.5
        -1.0,  # 9: leaf
        0.5,  # 10: x1 <= 0.5
        -1.0,  # 11: leaf
        0.5,  # 12: x2 <= 0.5
        -1.0,  # 13: leaf
        -1.0,  # 14: leaf
    ],
    value=[
        0.0,  # 0 internal
        0.0,  # 1
        0.0,  # 2 leaf
        0.0,  # 3
        0.0,  # 4 leaf
        0.0,  # 5
        0.0,  # 6 leaf
        1.0,  # 7 leaf
        0.0,  # 8
        10.0,  # 9 leaf
        0.0,  # 10
        10.0,  # 11 leaf
        0.0,  # 12
        10.0,  # 13 leaf
        11.0,  # 14 leaf
    ],
    weighted_n_node_samples=[
        16.0,  # 0
        8.0,  # 1
        4.0,  # 2
        4.0,  # 3
        2.0,  # 4
        2.0,  # 5
        1.0,  # 6
        1.0,  # 7
        8.0,  # 8
        4.0,  # 9
        4.0,  # 10
        2.0,  # 11
        2.0,  # 12
        1.0,  # 13
        1.0,  # 14
    ],
    split_type=[0] * 15,  # Only numeric splits
    categories_nodes=[],
    categories=[],
    categories_segments=[],
    categories_sizes=[],
)
