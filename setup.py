from setuptools import setup, find_packages

setup(
    name="chatsgp",
    version="0.1.0",
    description="Chat-based Stochastic Generation Planning - A multi-agent system for renewable energy optimization",
    packages=find_packages(),
    install_requires=[
        "openai>=1.21.0",
        "pulp>=2.8.0",
        "pandas>=2.0.0",
        "numpy>=1.26.0",
        "pyyaml>=6.0.1",
        "tqdm>=4.60.0",
    ],
    python_requires=">=3.7",
)

