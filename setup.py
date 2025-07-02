#!/usr/bin/env python3
"""
Setup script for Mouse Automation Toolkit
"""

from setuptools import setup, find_packages
import os

def read_requirements():
    """Read requirements from requirements.txt"""
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def read_readme():
    """Read README.md for long description"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Mouse Automation Toolkit - A comprehensive tool for recording, transforming, and replaying mouse actions"

setup(
    name="mouse-automation-toolkit",
    version="1.0.0",
    author="Christopher Q2nz Tims",
    description="A comprehensive tool for recording, transforming, and replaying mouse actions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=read_requirements(),
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "mouse-automation=main:main",
        ],
    },
    keywords="mouse automation recording playback gui testing",
    project_urls={
        "Bug Reports": "https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit/issues",
        "Source": "https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit",
    },
)