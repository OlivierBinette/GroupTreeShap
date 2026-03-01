#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>

#include "../lib/treeshap_xgb.hpp"

PYBIND11_MODULE(treeshap, m) {

    m.attr("__name__") = "grouptreeshap.treeshap";

    // Bind the tree_shap_xgb function
    m.def("treeshap_xgb", &treeshap_xgb,
          "XGBoost-like implementation of the TreeSHAP algorithm.",
          py::arg("tree"), py::arg("x"), py::arg("x_missing"), py::arg("phi"),
          py::arg("condition"), py::arg("condition_feature"),
          py::arg("feature_reprs"));
}