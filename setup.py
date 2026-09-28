from setuptools import setup, find_packages

setup(
    name="sparsiz",
    version="0.6.0",
    description="The Last Dance — Omni-Kernel AI Architecture (Sparsiz research prototype)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "torch",
        "numpy",
        "scipy",
        "networkx",
        "pyyaml",
        "toml",
        "prometheus_client",
        "grpcio",
        "protobuf",
    ],
    extras_require={
        "dev": ["pytest", "black", "mypy"]
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "rajaram-daemon=sparsiz.rajaram:main",
            "sparsiz-sim=sparsiz.simulations.compute_grid:main",
        ]
    }
)
