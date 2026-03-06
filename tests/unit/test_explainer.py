import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from tests.resources.tree_examples import (
    TREE_TWO_DEP_ONE_INDEP,
    TREE_THREE_DEP_ONE_INDEP,
)

from grouptreeshap.explainer import GroupedTreeExplainer
from grouptreeshap.tree_ensemble import TreeEnsemble
from grouptreeshap.tree import Tree


def test_three_features_tree_groupshap_values():
    tree = Tree(**TREE_TWO_DEP_ONE_INDEP)
    tree_ensemble = TreeEnsemble([tree])
    explainer = GroupedTreeExplainer(tree_ensemble)

    np.testing.assert_equal(explainer.shap_values([1, 1, 1], [0, 0, 2]), [3 / 4, 0, 5])
    np.testing.assert_equal(
        explainer.shap_values([1, 1, 1], feature_reprs=[1, 1, 2]), [0, 3 / 4, 5]
    )

    np.testing.assert_equal(
        explainer.shap_values([1, 0, 1], [0, 1, 1]), [0.125, 4.625, 0]
    )


def test_four_features_tree_groupshap_values():
    tree = Tree(**TREE_THREE_DEP_ONE_INDEP)
    tree_ensemble = TreeEnsemble([tree])
    explainer = GroupedTreeExplainer(tree_ensemble)

    # Manually-calculated groupSHAP value, which is also equal to groupwise sum-of-shap
    # due to feature independence between groups
    np.testing.assert_equal(
        explainer.shap_values([1, 1, 1, 1], [0, 0, 0, 3]), [0.875, 0, 0, 5]
    )
    np.testing.assert_almost_equal(
        explainer.shap_values([1, 1, 1, 1], [0, 1, 2, 3]),
        [0.875 / 3, 0.875 / 3, 0.875 / 3, 5],
        decimal=6,
    )

    # Check that groupSHAP do not equal groupwise sum-of-shap when there are interactions across groups
    np.testing.assert_equal(
        explainer.shap_values([1, 1, 1, 1], [0, 0, 2, 3]), [0.5625, 0, 0.3125, 5]
    )
    with pytest.raises(Exception):
        np.testing.assert_almost_equal(
            explainer.shap_values([1, 1, 1, 1], [0, 1, 2, 3]),
            [0.5625 / 2, 0.5625 / 2, 0.3125, 5],
            decimal=2,
        )


def test_init_with_tree_ensemble():
    ensemble = TreeEnsemble(trees=[])
    explainer = GroupedTreeExplainer(ensemble)

    assert explainer.tree_ensemble is ensemble
    np.testing.assert_equal(explainer.shap_values([]), [])
    np.testing.assert_equal(explainer.shap_values([], feature_reprs=[]), [])


def test_init_rejects_invalid_model():
    with pytest.raises(RuntimeError):
        GroupedTreeExplainer(object())


def test_init_with_model_get_booster():
    booster = MagicMock()
    model = MagicMock()
    model.get_booster.return_value = booster

    ensemble = TreeEnsemble([])

    with patch(
        "grouptreeshap.explainer.TreeEnsemble.from_xgboost", return_value=ensemble
    ) as m:
        explainer = GroupedTreeExplainer(model)
        m.assert_called_once_with(booster)

    assert explainer.tree_ensemble is ensemble


def test_init_with_booster_object():
    Booster = type("Booster", (), {})
    booster = Booster()

    ensemble = TreeEnsemble([])

    with patch(
        "grouptreeshap.explainer.TreeEnsemble.from_xgboost", return_value=ensemble
    ) as m:
        explainer = GroupedTreeExplainer(booster)
        m.assert_called_once_with(booster)

    assert explainer.tree_ensemble is ensemble
