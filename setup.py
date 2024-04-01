#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'PyYAML',
    'aiofiles',
    'aiohttp'
]

setup(
    name='trade-lib',
    description="我的交易库",
    version='0.1.3',
    py_modules=['trade_lib'],
    packages=find_packages(exclude=["tests"]),
    install_requires=install_requires,
)
