"""
SARAI Setup
===========

Synthetic Agentic Recursive Artificial Intelligence
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sarai",
    version="0.1.0",
    author="John Fizer",
    author_email="john.fizer@sarai.ai",
    description="Synthetic Agentic Recursive Artificial Intelligence - A developmental AI framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/john-fizer/SAIRA",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "full": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "neo4j>=5.0.0",
            "redis>=4.5.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.22.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "sarai=sarai.scripts.cli:main",
        ],
    },
)
