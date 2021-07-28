#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='chassisml',
    version='0.0.1',
    author='Carlos Millán Soler',
    author_email='cmillan@sciling.com',
    description='Python API client for Chassis.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['requests'],
    zip_safe=False,
)
