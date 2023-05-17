#!/usr/bin/env python
from os.path import exists

from setuptools import setup

import versioneer

setup(
    name="etuples",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Python S-expression emulation using tuple-like objects.",
    url="http://github.com/pythological/etuples",
    maintainer="Brandon T. Willard",
    maintainer_email="brandonwillard+etuples@gmail.com",
    packages=["etuples"],
    install_requires=[
        "cons",
        "multipledispatch",
    ],
    long_description=open("README.md").read() if exists("README.md") else "",
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
