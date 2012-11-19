#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import os


def read_file(*path):
    base_dir = os.path.dirname(__file__)
    file_path = (base_dir, ) + tuple(path)
    return file(os.path.join(*file_path)).read()

setup(
    name="redis-shard",
    url="http://blog.flyzen.com",
    license="BSD",
    author="Young King",
    author_email="yanckin@gmail.com",
    description="Redis Sharding API",
    long_description=(
        read_file("README.rst") + "\n\n" +
        "Change History\n" +
        "==============\n\n" +
        read_file("CHANGES.rst")),
    version="0.1.7",
    packages=["redis_shard"],
    include_package_data=True,
    zip_safe=False,
    install_requires=['redis', ],
    tests_require=['Nose'],
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
