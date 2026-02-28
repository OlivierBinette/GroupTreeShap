#pragma once

#include <cassert>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <stdexcept>

namespace py = pybind11;

using namespace std;

static constexpr int kFlags = py::array::c_style | py::array::forcecast;
template <typename T>
using pyarray = py::array_t<T, kFlags>;


class Tree {
public:
    pyarray<int> feature;
    pyarray<int> children_left;
    pyarray<int> children_right;
    pyarray<bool> missing_go_to_left;
    pyarray<double> threshold;
    pyarray<double> value;
    pyarray<double> weighted_n_node_samples;
    pyarray<int> split_type;
    pyarray<int> categories_nodes;
    pyarray<int> categories;
    pyarray<int> categories_segments;
    pyarray<int> categories_sizes;

    Tree(
        pyarray<int> feature,
        pyarray<int> children_left,
        pyarray<int> children_right,
        pyarray<bool> missing_go_to_left,
        pyarray<double> threshold,
        pyarray<double> value,
        pyarray<double> weighted_n_node_samples,
        pyarray<int> split_type,
        pyarray<int> categories_nodes,
        pyarray<int> categories,
        pyarray<int> categories_segments,
        pyarray<int> categories_sizes
    )
    : feature(feature),
      children_left(children_left),
      children_right(children_right),
      missing_go_to_left(missing_go_to_left),
      threshold(threshold),
      value(value),
      weighted_n_node_samples(weighted_n_node_samples),
      split_type(split_type),
      categories_nodes(categories_nodes),
      categories(categories),
      categories_segments(categories_segments),
      categories_sizes(categories_sizes)
    {
        validate();
    }

    void validate() const {
        // Check dimensions
        assert(feature.ndim() == 1);
        assert(children_left.ndim() == 1);
        assert(children_right.ndim() == 1);
        assert(missing_go_to_left.ndim() == 1);
        assert(threshold.ndim() == 1);
        assert(value.ndim() == 1);
        assert(weighted_n_node_samples.ndim() == 1);
        assert(split_type.ndim() == 1);
        assert(categories_nodes.ndim() == 1);
        assert(categories.ndim() == 1);
        assert(categories_segments.ndim() == 1);
        assert(categories_sizes.ndim() == 1);
        
        // Check sizes
        int n_nodes = feature.shape(0);
        assert(children_left.shape(0) == n_nodes);
        assert(children_right.shape(0) == n_nodes);
        assert(missing_go_to_left.shape(0) == n_nodes);
        assert(threshold.shape(0) == n_nodes);
        assert(value.shape(0) == n_nodes);
        assert(weighted_n_node_samples.shape(0) == n_nodes);
        assert(split_type.shape(0) == n_nodes);
        
        int n_cat_nodes = categories_nodes.shape(0);
        assert(categories_segments.shape(0) == n_cat_nodes);
        assert(categories_sizes.shape(0) == n_cat_nodes);

        // Check children indices are valid
        for (int i = 0; i < n_nodes; i++) {
            assert(children_left.at(i) < n_nodes);
            assert(children_right.at(i) < n_nodes);
        }

        // Check categories indices are valid
        for (ssize_t i = 0; i < n_cat_nodes; ++i) {
            assert(categories_segments.at(i) + categories_sizes.at(i) <= categories.shape(0));
        }
    }

    uint32_t max_depth() const {
        if (children_left.shape(0) == 0) {
            return 0;
        }

        vector<pair<uint32_t, uint32_t>> stack;
        stack.emplace_back(0, 0);

        uint32_t max_depth = 0;

        while (!stack.empty()) {
            auto [node, d] = stack.back();
            stack.pop_back();

            int l = children_left.at(node);
            int r = children_right.at(node);

            if (l < 0 && r < 0) {
                max_depth = max(max_depth, d);
                continue;
            }

            if (l >= 0) stack.emplace_back(l, d + 1);
            if (r >= 0) stack.emplace_back(r, d + 1);
        }

        return max_depth;
    }
};
