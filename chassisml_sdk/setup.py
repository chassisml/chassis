#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='chassisml',
    version='1.4.9',
    author='Carlos Millán Soler',
    author_email='cmillan@sciling.com',
    description='Python API client for Chassis.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={
        "": ["*.pyi"]
    },    
    python_requires='>=3.6',
    install_requires=['requests','mlflow','numpy','pyyaml~=6.0','validators','grpcio-tools~=1.50.0', 'grpclib~=0.4.3', 'docker~=6.0.1','protobuf~=4.21.9'],
    url='https://github.com/modzy/chassis/tree/main/chassisml_sdk',
    zip_safe=False,
)