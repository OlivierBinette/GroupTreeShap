from setuptools import setup, find_packages
from pybind11.setup_helpers import build_ext, intree_extensions

ext_modules = intree_extensions(
    [
        "src/grouptreeshap/shap/_cpp/treeshap.cpp",
    ]
)

setup(
    ext_modules=ext_modules,
    name="grouptreeshap",
    version="0.1.0",
    author="Olivier Binette",
    author_email="olivier.binette@upstart.com",
    url="https://github.com/OlivierBinette-Upstart/TreeTools",
    include_package_data=True,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=2",
        "pybind11>=3",
    ],
    extras_require={
        "test": [
            "pytest",
            "testbook",
            "ipykernel",
            "jupyter",
            "ipython",
            "scikit-learn",
            "shap",
            "matplotlib",
            "plotly",
            "xgboost",
        ],
        "dev": [
            "ruff",
        ],
    },
    cmdclass={"build_ext": build_ext},
)
