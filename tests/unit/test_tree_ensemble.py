import numpy as np

from tests.resources.xgb_export_example import XGB_EXPORT_EXAMPLE

from grouptreeshap.tree_ensemble import TreeEnsemble
from unittest.mock import MagicMock

def test_from_xgboost():
    ubj = XGB_EXPORT_EXAMPLE[0]

    booster = MagicMock()
    booster.save_raw = lambda *args, **kwargs: ubj

    tree_ensemble = TreeEnsemble.from_xgboost(booster)
    assert len(tree_ensemble.trees) == 1

    tree = tree_ensemble.trees[0]
    np.testing.assert_equal(tree.value, [-1.4470355154116987e-06, -23.804027557373047, 22.888486862182617])
    np.testing.assert_equal(tree.split_type, [0,0,0])
    np.testing.assert_equal(tree.threshold, np.nextafter(np.array([0.003770889015868306, -23.804027557373047, 22.888486862182617], dtype=np.float32), -np.float32(np.inf)))
    np.testing.assert_equal(tree.children_left, [1, -1, -1])
    np.testing.assert_equal(tree.children_right, [2, -1, -1])
    np.testing.assert_equal(tree.feature, [3, 0, 0])
    np.testing.assert_equal(tree.weighted_n_node_samples, [100.0, 49.0, 51.0])
    np.testing.assert_equal(tree.missing_go_to_left, [False, False, False])
    np.testing.assert_equal(tree.categories, [])
    np.testing.assert_equal(tree.categories_nodes, [])
    np.testing.assert_equal(tree.categories_segments, [])
    np.testing.assert_equal(tree.categories_sizes, [])
