#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

setup(
    name='chassisml',
    version='0.0.1',
    author='Modzy',
    author_email='support@modzy.com',
    description='Python API client for Chassis.',
    packages=find_packages(),
    python_requires='>=3.4',
    install_requires=['requests'],
    zip_safe=False,
)
