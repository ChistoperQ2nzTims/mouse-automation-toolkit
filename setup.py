#!/usr/bin/env python3
"""
Mouse Automation Toolkit Setup Script
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="mouse-automation-toolkit",
    version="1.0.0",
    author="Mouse Automation Toolkit Team",
    author_email="info@mouseautomation.com",
    description="A complete mouse automation toolkit with recording, transformation, and replay capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'mouse-automation=main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)