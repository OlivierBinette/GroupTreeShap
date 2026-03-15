import numpy as np

from grouptreeshap.treeshap import treeshap_xgb
from grouptreeshap.tree_ensemble import TreeEnsemble


class GroupedTreeExplainer:
    """
    Compute grouped TreeShap values for tree ensembles.

    This explainer wraps a tree-based model and computes SHAP values using the
    GroupTreeSHAP algorithm implemented in the underlying C++ extension.
    """

    def __init__(self, model: any) -> None:
        """
        Parameters
        ----------
        model : TreeEnsemble, xgboost.Booster, xgboost.XGBRegressor, or xgboost.XGBClassifier
            Only supports single-target models.
        """
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
        feature_reprs: list[int] | None = None,
    ) -> list[float]:
        """
        Compute grouped TreeShap values for a single input sample.

        Parameters
        ----------
        x : list[float]
            Feature values for the sample to explain.

        feature_reprs : list[int], optional
            Feature grouping representation. Each element maps an input
            feature to its group index. If ``None``, each feature is treated
            as its own group.

        Returns
        -------
        list[float]
            SHAP values corresponding to each feature (or feature group).
        """
        if feature_reprs is None:
            feature_reprs = list(range(len(x)))

        phi = np.zeros(len(x), dtype=np.float32)
        this_tree_contribs = np.zeros(len(x), dtype=np.float32)
        for tree in self.tree_ensemble.trees:
            this_tree_contribs *= 0
            treeshap_xgb(
                tree,
                x,
                this_tree_contribs,
                0,
                feature_reprs[0],
                feature_reprs=feature_reprs,
            )
            phi += this_tree_contribs

        return phi
