#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>

#include "treeshap_xgb.hpp"

PYBIND11_MODULE(treeshap, m) {

    m.attr("__name__") = "grouptreeshap.shap._cpp.treeshap";

    // Bind the Tree class
    py::class_<Tree>(m, "Tree")
        .def(py::init<
            py::array_t<int>,       // feature
            py::array_t<int>,       // children_left
            py::array_t<int>,       // children_right
            py::array_t<bool>,      // missing_go_to_left
            py::array_t<double>,    // threshold
            py::array_t<double>,    // value
            py::array_t<double>,    // weighted_n_node_samples
            py::array_t<int>,       // split_type
            py::array_t<int>,   // categories_nodes
            py::array_t<int>,   // categories
            py::array_t<int>,   // categories_segments
            py::array_t<int>    // categories_sizes
        >(),
            py::arg("feature"), 
            py::arg("children_left"), 
            py::arg("children_right"), 
            py::arg("missing_go_to_left"),
            py::arg("threshold"), 
            py::arg("value"), 
            py::arg("weighted_n_node_samples"),
            py::arg("split_type"),
            py::arg("categories_nodes"),
            py::arg("categories"),
            py::arg("categories_segments"),
            py::arg("categories_sizes")
        )
        .def_readwrite("feature", &Tree::feature)
        .def_readwrite("children_left", &Tree::children_left)
        .def_readwrite("children_right", &Tree::children_right)
        .def_readwrite("missing_go_to_left", &Tree::missing_go_to_left)
        .def_readwrite("threshold", &Tree::threshold)
        .def_readwrite("value", &Tree::value)
        .def_readwrite("weighted_n_node_samples", &Tree::weighted_n_node_samples)
        .def_readwrite("split_type", &Tree::split_type)
        .def_readwrite("categories_nodes", &Tree::categories_nodes)
        .def_readwrite("categories", &Tree::categories)
        .def_readwrite("categories_segments", &Tree::categories_segments)
        .def_readwrite("categories_sizes", &Tree::categories_sizes);

    // Bind the tree_shap_xgb function
    m.def("tree_shap_xgb", &tree_shap_xgb,
          "XGBoost-like implementation of the TreeSHAP algorithm.",
          py::arg("tree"), py::arg("x"), py::arg("x_missing"), py::arg("phi"),
          py::arg("condition"), py::arg("condition_feature"),
          py::arg("feature_reprs"));
}