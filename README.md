[![Test Package](https://github.com/OlivierBinette/GroupedTreeSHAP/actions/workflows/test.yaml/badge.svg)](https://github.com/OlivierBinette/GroupedTreeSHAP/actions/workflows/test.yaml)

# GroupTreeShap

Efficiently compute grouped (aka coalitions of) Shapley values ([Jullum et al., 2021](https://arxiv.org/abs/2106.12228); [Amoukou et al., 2021](https://export.arxiv.org/pdf/2103.13342v2)) for tree ensembles using a variant of the TreeShap algorithm ([Lundberg et al., 2019](https://arxiv.org/pdf/1802.03888)).

## Installation

Install from PyPI:
```sh
pip install grouptreeshap
```
This package includes a C++ extension built with [pybind11](https://pybind11.readthedocs.io/en/stable/). See 

## Usage

From an XGBoost `model` instance:
```python
from grouptreeshap import GroupedTreeExplainer

explainer = GroupedTreeExplainer(model)
phi = explainer.shap_values(X, feature_reprs)  # Grouped Shap values
```
Here `feature_reprs` is an optional *membership vector* associating each feature `i` to a group representative `feature_reprs[i]`. The Shap value of the group containing feature `i` is `phi[feature_reprs[i]]`.

If `feature_reprs = range(len(X))`, then all features are in their own distinct group and the Shap values are the same as the ones calculated by XGBoost.

## Currently Supported Models

- Models represented as `grouptreeshap.TreeEnsemble` instances.
- XGBoost regression and single-target classification models, specifically [`Booster`](xgboost), [`XGBRegressor`](https://xgboost.readthedocs.io/en/latest/python/python_api.html#xgboost.XGBRegressor), and [`XGBClassifier`](https://xgboost.readthedocs.io/en/latest/python/python_api.html#xgboost.XGBClassifier) instances. Categorical data is supported.

## Comparison to Summing Shap Values by Group

Summing feature-level Shap values by group is not equivalent to calculating groupShap values. [Here is an example](analyses/credit-card-default-example.ipynb) of differences between groupShap and sum-of-Shap for explaining a credit default prediction for a particular individual:

[![](analyses/groupShap%20comparison.png)](analyses/credit-card-default-example.ipynb)

## Testing and Validation

The implementation has been validated via:
- Examples where groupShap values have been calculated exactly by hand.
- Checks of exact equality with XGBoost's Shap value calculation, when each feature is in its own group.

## References

- [Jullum, M., Redelmeier, A., & Aas, K. (2021). groupShapley: Efficient prediction explanation with Shapley values for feature groups. arXiv preprint arXiv:2106.12228.](https://arxiv.org/abs/2106.12228)
- [Amoukou, S. I., Brunel, N. J., & Salaün, T. (2021). The shapley value of coalition of variables provides better explanations. arXiv preprint arXiv:2103.13342.](https://export.arxiv.org/pdf/2103.13342v2)
- [Lundberg, S. M., Erion, G. G., & Lee, S. I. (2018). Consistent individualized feature attribution for tree ensembles. arXiv preprint arXiv:1802.03888.](https://arxiv.org/pdf/1802.03888)
