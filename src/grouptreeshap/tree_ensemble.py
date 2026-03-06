import io
from dataclasses import dataclass

import numpy as np

from grouptreeshap.ubjson import UBJSONDecoder
from grouptreeshap.tree import Tree


@dataclass
class TreeEnsemble:
    trees: list[Tree]

    @classmethod
    def from_xgboost(cls, booster) -> "TreeEnsemble":
        raw = booster.save_raw(raw_format="ubj")
        with io.BytesIO(raw) as fd:
            jmodel = UBJSONDecoder(fd).decode()

        trees = jmodel["learner"]["gradient_booster"]["model"]["trees"]
        return cls(
            [
                Tree(
                    feature=t["split_indices"],
                    children_left=t["left_children"],
                    children_right=t["right_children"],
                    threshold=np.nextafter(
                        np.array(t["split_conditions"], dtype=np.float32),
                        -np.float32(np.inf),
                    ),
                    missing_go_to_left=t["default_left"],
                    value=np.array(t["base_weights"], dtype=np.float64),
                    weighted_n_node_samples=t["sum_hessian"],
                    split_type=t.get("split_type", [0] * len(t["split_indices"])),
                    categories_nodes=t.get("categories_nodes", []),
                    categories=t.get("categories", []),
                    categories_segments=t.get("categories_segments", []),
                    categories_sizes=t.get("categories_sizes", []),
                )
                for t in trees
            ]
        )
