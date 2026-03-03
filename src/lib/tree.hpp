#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <stdexcept>
#include <vector>
#include <utility>
#include <algorithm>
#include <cmath>

namespace grouptreeshap
{

    namespace py = pybind11;

    static constexpr int kFlags = py::array::c_style | py::array::forcecast;
    template <typename T>
    using pyarray = py::array_t<T, kFlags>;

    inline void check(bool cond, const char *msg)
    {
        if (!cond)
            throw py::value_error(msg);
    }

    class Tree
    {
    public:
        pyarray<int> feature;
        pyarray<int> children_left;
        pyarray<int> children_right;
        pyarray<bool> missing_go_to_left;
        pyarray<double> threshold;
        pyarray<double> value;
        pyarray<double> weighted_n_node_samples;
        pyarray<int> split_type; // 0 for numerical split, 1 for categorical split.
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
            pyarray<int> categories_sizes)
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

        void validate() const
        {
            // 1D checks
            check(feature.ndim() == 1, "feature is not 1d");
            check(children_left.ndim() == 1, "children_left is not 1d");
            check(children_right.ndim() == 1, "children_right is not 1d");
            check(missing_go_to_left.ndim() == 1, "missing_go_to_left is not 1d");
            check(threshold.ndim() == 1, "threshold is not 1d");
            check(value.ndim() == 1, "value is not 1d");
            check(weighted_n_node_samples.ndim() == 1, "weighted_n_node_samples is not 1d");
            check(split_type.ndim() == 1, "split_type is not 1d");
            check(categories_nodes.ndim() == 1, "categories_nodes is not 1d");
            check(categories.ndim() == 1, "categories is not 1d");
            check(categories_segments.ndim() == 1, "categories_segments is not 1d");
            check(categories_sizes.ndim() == 1, "categories_sizes is not 1d");

            int n_nodes = feature.shape(0);

            // Size checks
            check(children_left.shape(0) == n_nodes, "children_left has invalid length");
            check(children_right.shape(0) == n_nodes, "children_right has invalid length");
            check(missing_go_to_left.shape(0) == n_nodes, "missing_go_to_left has invalid length");
            check(threshold.shape(0) == n_nodes, "threshold has invalid length");
            check(value.shape(0) == n_nodes, "value has invalid length");
            check(weighted_n_node_samples.shape(0) == n_nodes, "weighted_n_node_samples has invalid length");
            check(split_type.shape(0) == n_nodes, "split_type has invalid length");

            int n_cat_nodes = categories_nodes.shape(0);
            check(categories_segments.shape(0) == n_cat_nodes, "categories_segments has invalid length");
            check(categories_sizes.shape(0) == n_cat_nodes, "categories_sizes has invalid length");

            // Tree checks
            for (int i = 0; i < n_nodes; ++i)
            {
                int l = children_left.at(i);
                int r = children_right.at(i);
                check(l < n_nodes, "children_left out of bound");
                check(r < n_nodes, "children_right out of bound");
                check(l != i && r != i, "child points to self");

                bool leaf = (l < 0 && r < 0);
                bool internal = (l >= 0 && r >= 0);
                check(leaf || internal, "Invalid node type");

                check(leaf || feature.at(i) >= 0, "Invalid feature index");

                check(weighted_n_node_samples.at(i) >= 0, "weighted_n_node_samples should be non-negative");
            }

            // Categorical data checks
            int n_cat = categories.shape(0);
            for (int i = 0; i < n_cat_nodes; ++i)
            {
                check(categories_nodes.at(i) >= 0 && categories_nodes.at(i) < n_nodes, "categories_nodes out of bounds");
                check(categories_segments.at(i) >= 0, "categories_segments should be non-negative");
                check(categories_sizes.at(i) >= 0, "categories_sizes should be non-negative");
                check(categories_segments.at(i) + categories_sizes.at(i) <= n_cat, "categories_segments out of bounds");
            }
        }

        int get_next_node(int start_node, const pyarray<double> &x) const
        {
            int split_index = feature.at(start_node);
            if (split_index < 0)
            {
                return start_node;
            }

            int cleft = children_left.at(start_node);
            int cright = children_right.at(start_node);
            if (cleft < 0 && cright < 0)
            {
                return start_node;
            }

            if (std::isnan(x.at(split_index)))
            {
                if (missing_go_to_left.at(start_node))
                    return cleft;
                else
                    return cright;
            }
            else
            {
                float feature_value = x.at(split_index);
                if (split_type.at(start_node))
                { // categorical split
                    int i = 0;
                    while ((i < categories_nodes.shape(0)) && (categories_nodes.at(i) != start_node))
                    {
                        i++;
                    }
                    int start_seg = categories_segments.at(i);
                    int end_seg = start_seg + categories_sizes.at(i);
                    for (int j = start_seg; j < end_seg; ++j)
                    {
                        if (categories.at(j) == static_cast<int>(x.at(split_index)))
                        {
                            return cright;
                        }
                    }
                    return cleft;
                }
                else
                { // numerical split
                    if (feature_value <= threshold.at(start_node))
                    {
                        return cleft;
                    }
                    else
                    {
                        return cright;
                    }
                }
            }
        }

        int depth() const
        {
            if (children_left.shape(0) == 0)
            {
                return 0;
            }

            std::vector<std::pair<int, int>> stack;
            stack.emplace_back(0, 0);

            int depth = 0;

            while (!stack.empty())
            {
                int node = stack.back().first;
                int d = stack.back().second;
                stack.pop_back();

                int l = children_left.at(node);
                int r = children_right.at(node);

                if (l < 0 && r < 0)
                {
                    depth = std::max(depth, d);
                    continue;
                }

                if (l >= 0)
                    stack.emplace_back(l, d + 1);
                if (r >= 0)
                    stack.emplace_back(r, d + 1);
            }

            return depth;
        }
    };
} // namespace grouptreeshap