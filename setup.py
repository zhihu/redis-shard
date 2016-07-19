# -*- coding: utf-8 -*-

import os
from setuptools import setup

import redis_shard


def read_file(*path):
    base_dir = os.path.dirname(__file__)
    file_path = (base_dir, ) + tuple(path)
    return open(os.path.join(*file_path)).read()

setup(
    name="redis-shard",
    url="https://github.com/zhihu/redis-shard",
    license="BSD License",
    author="Zhihu Inc.",
    author_email="opensource@zhihu.com",
    maintainer="Young King",
    maintainer_email="y@zhihu.com",
    description="Redis Sharding API",
    long_description=(
        read_file("README.rst") + "\n\n" +
        "Change History\n" +
        "==============\n\n" +
        read_file("CHANGES.rst")),
    version=redis_shard.__version__,
    packages=["redis_shard"],
    include_package_data=True,
    zip_safe=False,
    install_requires=['redis>=2.10.5'],
    tests_require=['Nose'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
