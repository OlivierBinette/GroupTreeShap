from dataclasses import dataclass, field


@dataclass
class Tree:
    feature: list[int]
    children_left: list[int]
    children_right: list[int]
    missing_go_to_left: list[bool]
    threshold: list[float]
    value: list[float]
    weighted_n_node_samples: list[float]
    split_type: list[str]

    categories_nodes: list[int] = field(default_factory=list)
    categories: list[int] = field(default_factory=list)
    categories_segments: list[int] = field(default_factory=list)
    categories_sizes: list[int] = field(default_factory=list)
