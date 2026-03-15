#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "../lib/tree.hpp"

using namespace grouptreeshap;
namespace py = pybind11;

PYBIND11_MODULE(tree, m) {

    m.attr("__name__") = "grouptreeshap.tree";

    py::class_<Tree>(m, "Tree", R"pbdoc(
Decision tree structure used by GroupTreeShap.

This class represents a tree in a flat array format similar to the
internal representation used by many gradient boosting libraries.
Each node is indexed by position in the arrays.
)pbdoc")
        .def(py::init<
                py::array_t<int>,        // feature
                py::array_t<int>,        // children_left
                py::array_t<int>,        // children_right
                py::array_t<bool>,       // missing_go_to_left
                py::array_t<double>,     // threshold
                py::array_t<double>,     // value
                py::array_t<double>,     // weighted_n_node_samples
                py::array_t<int>,        // split_type
                py::array_t<int>,        // categories_nodes
                py::array_t<int>,        // categories
                py::array_t<int>,        // categories_segments
                py::array_t<int>         // categories_sizes
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

        .def_readwrite(
            "feature",
            &Tree::feature,
            "Feature index used for splitting at each node. "
            "Leaf nodes should use a negative number."
        )

        .def_readwrite(
            "children_left",
            &Tree::children_left,
            "Index of the left child node for each node. "
            "Leaf nodes should use a negative number."
        )

        .def_readwrite(
            "children_right",
            &Tree::children_right,
            "Index of the right child node for each node. "
            "Leaf nodes should use a negative number."
        )

        .def_readwrite(
            "missing_go_to_left",
            &Tree::missing_go_to_left,
            "Indicates whether missing feature values follow the left branch."
        )

        .def_readwrite(
            "threshold",
            &Tree::threshold,
            "Threshold value used for numerical splits."
        )

        .def_readwrite(
            "value",
            &Tree::value,
            "Prediction value stored at each node. For leaf nodes this "
            "corresponds to the output value of the tree."
        )

        .def_readwrite(
            "weighted_n_node_samples",
            &Tree::weighted_n_node_samples,
            "Weighted number of training samples that reached each node."
        )

        .def_readwrite(
            "split_type",
            &Tree::split_type,
            "Type of split used at each node: 1 for numerical, 0 for categorical."
        )

        .def_readwrite(
            "categories_nodes",
            &Tree::categories_nodes,
            "List of the indices of categorical nodes."
        )

        .def_readwrite(
            "categories",
            &Tree::categories,
            "Flattened list of category values used for categorical splits."
        )

        .def_readwrite(
            "categories_segments",
            &Tree::categories_segments,
            "Start offsets of categorical segments within the `categories` array."
        )

        .def_readwrite(
            "categories_sizes",
            &Tree::categories_sizes,
            "Number of categories associated with each categorical split node."
        );
}