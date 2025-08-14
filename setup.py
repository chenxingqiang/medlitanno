#!/usr/bin/env python3
"""
Setup script for MedLitAnno - Medical Literature Analysis and Annotation System
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="medlitanno",
    version="1.1.0",
    author="Chen Xingqiang",
    author_email="joy66777@gmail.com",
    description="Medical Literature Analysis and Annotation System with LLM-powered automation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/chenxingqiang/medlitanno",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "web": [
            "streamlit>=1.28.0",
            "plotly>=5.17.0",
        ],
        "mragent": [
            "biopython>=1.81",
            "rpy2>=3.5.0",
        ],
        "full": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "streamlit>=1.28.0",
            "plotly>=5.17.0",
            "biopython>=1.81",
            "rpy2>=3.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "medlitanno=medlitanno.cli:main",
            "medlitanno-annotate=medlitanno.annotation.cli:main",
            "medlitanno-mr=medlitanno.mragent.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "medlitanno": [
            "data/*.csv",
            "templates/*.txt",
            "config/*.json",
        ],
    },
    keywords=[
        "medical literature",
        "annotation",
        "pubmed search",
        "mendelian randomization",
        "llm",
        "biomedical nlp",
        "causal inference",
        "gwas",
        "automation",
        "literature mining",
    ],
    project_urls={
        "Bug Reports": "https://github.com/chenxingqiang/medlitanno/issues",
        "Source": "https://github.com/chenxingqiang/medlitanno",
        "Documentation": "https://github.com/chenxingqiang/medlitanno/blob/main/docs/",
    },
)