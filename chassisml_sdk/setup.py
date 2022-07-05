#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='chassisml',
    version='1.4.4',
    author='Carlos Millán Soler',
    author_email='cmillan@sciling.com',
    description='Python API client for Chassis.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['requests','mlflow','numpy','pyyaml','validators','grpc-requests','grpcio>=1.44.0','docker','protobuf==3.19.4'],
    url='https://github.com/modzy/chassis/tree/main/chassisml_sdk',
    zip_safe=False,
)
