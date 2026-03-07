import sys
from setuptools import setup, find_packages
from pybind11.setup_helpers import build_ext, intree_extensions

ext_modules = intree_extensions(
    [
        "src/grouptreeshap/tree.cpp",
        "src/grouptreeshap/treeshap.cpp",
    ]
)

for ext in ext_modules:
    ext.cxx_std = 17
    if sys.platform in ["linux"]:
        ext.extra_compile_args = ["-O2", "-ffp-contract=fast"]

setup(
    ext_modules=ext_modules,
    name="grouptreeshap",
    version="0.1.0",
    author="Olivier Binette",
    author_email="olivier.binette@upstart.com",
    url="https://github.com/OlivierBinette-Upstart/TreeTools",
    include_package_data=True,
    packages=find_packages(where="src", include="grouptreeshap*"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=2",
        "pybind11>=3",
    ],
    extras_require={
        "integration": [
            "scikit-learn>=1.5",
            "xgboost>=3",
            "pandas>=2",
        ],
        "test": [
            "pytest",
            "testbook",
            "ipykernel",
            "jupyter",
            "ipython",
        ],
        "dev": [
            "hatch",
            "ruff",
            "pre-commit",
        ],
    },
    cmdclass={"build_ext": build_ext},
)
