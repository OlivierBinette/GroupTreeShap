from abc import ABC, abstractmethod
from grouptreeshap.shap._cpp.treeshap import Tree as CppTree, tree_shap_xgb

import numpy as np

from grouptreeshap.tree_ensemble import TreeEnsemble


class Explainer(ABC):
    def __init__(self, model: any) -> None:
        if isinstance(model, TreeEnsemble):
            self.tree_ensemble = model
        elif hasattr(model, "get_booster"):
            self.tree_ensemble = TreeEnsemble.from_xgboost(model.get_booster())
        elif model.__class__.__name__ == "Booster":
            self.tree_ensemble = TreeEnsemble.from_xgboost(model)
        else:
            raise RuntimeError(f"Unsupported model: {model}")
        
    @abstractmethod
    def shap_values(self, x: list[float], **kwargs) -> list[float]: ...


class GroupedTreeExplainer(Explainer):
    def shap_values(
        self,
        x: list[float],
        x_missing: list[int] | None = None,
        feature_reprs: list[int] | None = None,
    ) -> list[float]:
        if feature_reprs is None:
            feature_reprs = list(range(len(x)))

        if x_missing is None:
            x_missing = np.isnan(x)

        cpp_trees = [
            CppTree(
                tree.feature,
                tree.children_left,
                tree.children_right,
                tree.missing_go_to_left,
                tree.threshold,
                tree.value,
                tree.weighted_n_node_samples,
                tree.split_type,
                tree.categories_nodes,
                tree.categories,
                tree.categories_segments,
                tree.categories_sizes,
            )
            for tree in self.tree_ensemble.trees
        ]

        phi = np.zeros(len(x), dtype=np.float32)
        this_tree_contribs = np.zeros(len(x), dtype=np.float32)
        for tree in cpp_trees:
            this_tree_contribs *= 0
            tree_shap_xgb(tree, x, x_missing, this_tree_contribs, 0, feature_reprs[0], feature_reprs=feature_reprs)
            phi += this_tree_contribs

        return phi
