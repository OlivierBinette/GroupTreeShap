INVALID_EXAMPLES = [
    # Multiple values/containers
    b'ZZ',
    b'TF',
    b'i\x01i\x02',
    b'T[TF]',
    b'[TF]T',
    b'[TF][FT]',

    # Unexpected end of sequence
    b'N',
    b'[TF',
    b'[[]',
    b'I\x00',
    b'Si\x03ab',
    b'{i\x05firsti\x01',
    
    # Invalid
    (
        b'['
          b'[i\x01i\x02]'
          b'i\x03]'
        b']'  # Extraneous closing brace
    ),
    (
        b'[#i\x03'
            b'i\x01'
            b'i\x02'
            b'i\x03'
        b']'  # Extraneous closing brace
    ),
    (  # Ambiguous specification
        b'[$[#i\x02'
            b'#i\x02i\x01i\x02'
            b'$i#i\x01\x03'
    ),
]

UBJSON_EXAMPLES = [
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
    (b'd\x3f\x80\x00\x00', 1.0),
    (b'd\x3f\xc0\x00\x00', 1.5),
    (b'd\xc0\xd9\x99\x9a', -6.800000190734863),
    (b'd\xc7\xf1\x20\x60', -123456.75),
    (b'dB\xc8\x00\x00', 100.0),

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

    # Unoptimized mixed array with no-ops: [null, true, "hi", 42]
    # [ [Z] [T] [S][i][2][hi] [N] [i][42] [N] ]
    (b'[ZTSi\x02hiNi\x2aN]', [None, True, "hi", 42]),

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
    (
        b'[#i\x03'
            b'i\x01'
            b'i\x02'
            b'i\x03', 
        [1, 2, 3]
    ),

    # Nested counts
    (
        b'[$[#i\x02#i\x03'
            b'TF'
            b'FT'
            b'TT',
        [[True, False], [False, True], [True, True]]
    ),

    # Optimized with type + count: float32 array
    # [ [$][d][#][i][4]  [1.0] [2.0] [1.5] [100.0]
    (
        b'[$d#i\x04'
            b'\x3f\x80\x00\x00'
            b'\x40\x00\x00\x00'
            b'\x3f\xc0\x00\x00'
            b'B\xc8\x00\x00',
        [1.0, 2.0, 1.5, 100.0]
    ),

    # Strongly typed nested arrays
    (
        b'[$[#i\x02'
            b'$i#i\x02\x01\x02'
            b'$i#i\x01\x03',
        [[1, 2], [3]]
    ),
    (
        b'[$[$i#i\x02#i\x02'
            b'\x01\x02'
            b'\x03\x04',
        [[1, 2], [3, 4]]
    ),
    (
        b'[$[#i\x02#i\x02'
            b'i\x01i\x02'
            b'i\x03i\x04',
        [[1, 2], [3, 4]]
    ),
    (
        b'[$[#i\x02'
            b'[$i#i\x02\x01\x02]'
            b'[$i#i\x02\x03\x04]',
        [[[1, 2]], [[3, 4]]]
    ),
    (
        b'[$[#i\x02'
            b'i\x01i\x02]'
            b'i\x03]',
        [[1, 2], [3]]
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

    # -------
    # Objects
    # -------

    # Unoptimized object
    (
        b'{'
            b'i\x05firstd\x3f\xc0\x00\x00'
            b'i\x06secondSi\06second'
            b'i\x05thirdZ'
        b'}',
        ({"first": 1.5, "second": "second", "third": None})
    ),

    # Object with count
    (
        b'{#i\x03'
            b'i\x05firstd\x3f\xc0\x00\x00'
            b'i\x06secondSi\06second'
            b'i\x05thirdZ',
        ({"first": 1.5, "second": "second", "third": None})
    ),

    # Object with type None
    (
        b'{$Z#i\x03'
            b'i\x05first'
            b'i\x06second'
            b'i\x05third',
        ({"first": None, "second": None, "third": None})
    ),

    # Object with type char
    (
        b'{$C#i\x03'
            b'i\x05firsta'
            b'i\x06secondb'
            b'i\x05thirdc',
        ({"first": "a", "second": "b", "third": "c"})
    ),

    # Strongly-typed nested objects
    (
        b'{${$i#i\x00#i\x03'
            b'i\x05first'
            b'i\x06second'
            b'i\x05third',
        ({"first": {}, "second": {}, "third": {}})
    ),
    (
        b'{$[$T#i\x01#i\x03'
            b'i\x05first'
            b'i\x06second'
            b'i\x05third',
        ({"first": [True], "second": [True], "third": [True]})
    ),
    (
        b'{$[$i#i\x02#i\x03'
            b'i\x05first\x01\x02'
            b'i\x06second\x03\x04'
            b'i\x05third\x05\x06',
        ({"first": [1,2], "second": [3,4], "third": [5,6]})
    ),
    (  # XGBoost example
        b'{L\x00\x00\x00\x00\x00\x00\x00\x07learner{L\x00\x00\x00\x00\x00\x00\x00\nattributes{}L\x00\x00\x00\x00\x00\x00\x00\rfeature_names[#L\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\rfeature_types[#L\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x10gradient_booster{L\x00\x00\x00\x00\x00\x00\x00\x05model{L\x00\x00\x00\x00\x00\x00\x00\x04cats{L\x00\x00\x00\x00\x00\x00\x00\x03enc[#L\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x10feature_segments[$l#L\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\nsorted_idx[$l#L\x00\x00\x00\x00\x00\x00\x00\x00}L\x00\x00\x00\x00\x00\x00\x00\x12gbtree_model_param{L\x00\x00\x00\x00\x00\x00\x00\x11num_parallel_treeSL\x00\x00\x00\x00\x00\x00\x00\x011L\x00\x00\x00\x00\x00\x00\x00\tnum_treesSL\x00\x00\x00\x00\x00\x00\x00\x011}L\x00\x00\x00\x00\x00\x00\x00\x10iteration_indptr[#L\x00\x00\x00\x00\x00\x00\x00\x02i\x00i\x01L\x00\x00\x00\x00\x00\x00\x00\ttree_info[#L\x00\x00\x00\x00\x00\x00\x00\x01i\x00L\x00\x00\x00\x00\x00\x00\x00\x05trees[#L\x00\x00\x00\x00\x00\x00\x00\x01{L\x00\x00\x00\x00\x00\x00\x00\x0cbase_weights[$d#L\x00\x00\x00\x00\x00\x00\x00\x03\xb5\xc27\xc3\xc1\xben\xa6A\xb7\x1b\x9fL\x00\x00\x00\x00\x00\x00\x00\ncategories[$l#L\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x10categories_nodes[$l#L\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x13categories_segments[$L#L\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x10categories_sizes[$L#L\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x0cdefault_left[$U#L\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x02idi\x00L\x00\x00\x00\x00\x00\x00\x00\rleft_children[$l#L\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xffL\x00\x00\x00\x00\x00\x00\x00\x0closs_changes[$d#L\x00\x00\x00\x00\x00\x00\x00\x03I\x16\xc0\xb4\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x07parents[$l#L\x00\x00\x00\x00\x00\x00\x00\x03\x7f\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x0eright_children[$l#L\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x02\xff\xff\xff\xff\xff\xff\xff\xffL\x00\x00\x00\x00\x00\x00\x00\x10split_conditions[$d#L\x00\x00\x00\x00\x00\x00\x00\x03;w!\x05\xc1\xben\xa6A\xb7\x1b\x9fL\x00\x00\x00\x00\x00\x00\x00\rsplit_indices[$l#L\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\nsplit_type[$U#L\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x0bsum_hessian[$d#L\x00\x00\x00\x00\x00\x00\x00\x03B\xc8\x00\x00BD\x00\x00BL\x00\x00L\x00\x00\x00\x00\x00\x00\x00\ntree_param{L\x00\x00\x00\x00\x00\x00\x00\x0bnum_deletedSL\x00\x00\x00\x00\x00\x00\x00\x010L\x00\x00\x00\x00\x00\x00\x00\x0bnum_featureSL\x00\x00\x00\x00\x00\x00\x00\x015L\x00\x00\x00\x00\x00\x00\x00\tnum_nodesSL\x00\x00\x00\x00\x00\x00\x00\x013L\x00\x00\x00\x00\x00\x00\x00\x10size_leaf_vectorSL\x00\x00\x00\x00\x00\x00\x00\x011}}}L\x00\x00\x00\x00\x00\x00\x00\x04nameSL\x00\x00\x00\x00\x00\x00\x00\x06gbtree}L\x00\x00\x00\x00\x00\x00\x00\x13learner_model_param{L\x00\x00\x00\x00\x00\x00\x00\nbase_scoreSL\x00\x00\x00\x00\x00\x00\x00\r[-6.359271E0]L\x00\x00\x00\x00\x00\x00\x00\x12boost_from_averageSL\x00\x00\x00\x00\x00\x00\x00\x011L\x00\x00\x00\x00\x00\x00\x00\tnum_classSL\x00\x00\x00\x00\x00\x00\x00\x010L\x00\x00\x00\x00\x00\x00\x00\x0bnum_featureSL\x00\x00\x00\x00\x00\x00\x00\x015L\x00\x00\x00\x00\x00\x00\x00\nnum_targetSL\x00\x00\x00\x00\x00\x00\x00\x011}L\x00\x00\x00\x00\x00\x00\x00\tobjective{L\x00\x00\x00\x00\x00\x00\x00\x04nameSL\x00\x00\x00\x00\x00\x00\x00\x10reg:squarederrorL\x00\x00\x00\x00\x00\x00\x00\x0ereg_loss_param{L\x00\x00\x00\x00\x00\x00\x00\x10scale_pos_weightSL\x00\x00\x00\x00\x00\x00\x00\x011}}}L\x00\x00\x00\x00\x00\x00\x00\x07version[#L\x00\x00\x00\x00\x00\x00\x00\x03i\x03i\x02i\x00}',
        {'learner': {'attributes': {},
        'feature_names': [],
        'feature_types': [],
        'gradient_booster': {'model': {'cats': {'enc': [],
            'feature_segments': [],
            'sorted_idx': []},
            'gbtree_model_param': {'num_parallel_tree': '1', 'num_trees': '1'},
            'iteration_indptr': [0, 1],
            'tree_info': [0],
            'trees': [{'base_weights': [-1.4470355154116987e-06,
            -23.804027557373047,
            22.888486862182617],
            'categories': [],
            'categories_nodes': [],
            'categories_segments': [],
            'categories_sizes': [],
            'default_left': [0, 0, 0],
            'id': 0,
            'left_children': [1, -1, -1],
            'loss_changes': [617483.25, 0.0, 0.0],
            'parents': [2147483647, 0, 0],
            'right_children': [2, -1, -1],
            'split_conditions': [0.003770889015868306,
            -23.804027557373047,
            22.888486862182617],
            'split_indices': [3, 0, 0],
            'split_type': [0, 0, 0],
            'sum_hessian': [100.0, 49.0, 51.0],
            'tree_param': {'num_deleted': '0',
            'num_feature': '5',
            'num_nodes': '3',
            'size_leaf_vector': '1'}}]},
        'name': 'gbtree'},
        'learner_model_param': {'base_score': '[-6.359271E0]',
        'boost_from_average': '1',
        'num_class': '0',
        'num_feature': '5',
        'num_target': '1'},
        'objective': {'name': 'reg:squarederror',
        'reg_loss_param': {'scale_pos_weight': '1'}}},
        'version': [3, 2, 0]}
    )
]