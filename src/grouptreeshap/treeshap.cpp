#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>

#include "../lib/treeshap_xgb.hpp"

using namespace grouptreeshap;

PYBIND11_MODULE(treeshap, m) {

    m.attr("__name__") = "grouptreeshap.treeshap";

    m.def(
        "treeshap_xgb", 
        &treeshap_xgb, 
        R"pbdoc(
Compute grouped TreeShap values for a single XGBoost-style decision tree.

This function applies a float32 implementation of the TreeSHAP algorithm
to a single tree and writes the resulting feature attributions into `phi`.

Parameters
----------
tree : grouptreeshap.tree.Tree
    Tree object containing the split structure, node values, sample weights,
    and optional categorical split metadata.

x : numpy.ndarray
    Input feature vector for the sample to be explained.

phi : numpy.ndarray
    Output array of SHAP values. This array is modified in place by the
    function. Its contents should be initialized by the caller to zeros.

condition : int
    Conditioning mode used by the TreeSHAP recursion.

condition_feature : int
    Feature index used for conditioning. This is relevant only
    when `condition` requests a conditioned explanation.

feature_reprs : numpy.ndarray
    Membership vector mapping each feature to a group representative.

Notes
-----
- The function mutates `phi` in place and does not return a value.
)pbdoc",
          "XGBoost-like float32 implementation of the TreeSHAP algorithm.",
          py::arg("tree"), py::arg("x"), py::arg("phi"),
          py::arg("condition"), py::arg("condition_feature"),
          py::arg("feature_reprs"));
}