#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

setup(
    name='chassisml',
    version='0.0.1',
    author='Carlos Millan Soler',
    author_email='cmillan@sciling.com',
    description='Python API client for Chassis.',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['requests'],
    zip_safe=False,
)
