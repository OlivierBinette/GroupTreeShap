import numpy as np

from grouptreeshap.treeshap import treeshap_xgb
from grouptreeshap.tree_ensemble import TreeEnsemble

class GroupedTreeExplainer:
    def __init__(self, model: any) -> None:
        if isinstance(model, TreeEnsemble):
            self.tree_ensemble = model
        elif hasattr(model, "get_booster"):
            self.tree_ensemble = TreeEnsemble.from_xgboost(model.get_booster())
        elif model.__class__.__name__ == "Booster":
            self.tree_ensemble = TreeEnsemble.from_xgboost(model)
        else:
            raise RuntimeError(f"Unsupported model: {model}")

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

        phi = np.zeros(len(x), dtype=np.float32)
        this_tree_contribs = np.zeros(len(x), dtype=np.float32)
        for tree in self.tree_ensemble.trees:
            this_tree_contribs *= 0
            treeshap_xgb(tree, x, x_missing, this_tree_contribs, 0, feature_reprs[0], feature_reprs=feature_reprs)
            phi += this_tree_contribs

        return phi
