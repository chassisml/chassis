#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='chassisml',
    version='1.4.0',
    author='Carlos Millán Soler',
    author_email='cmillan@sciling.com',
    description='Python API client for Chassis.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['requests','mlflow','numpy','pyyaml','validators','grpc-requests','docker',
                    'opencv-python-headless','onnxruntime','onnx','mxnet','boto3','xgboost==0.90.0','gluoncv','azureml-core>=1.41.0',
                    'azureml-automl-runtime','pandas'],
    url='https://github.com/modzy/chassis/tree/main/chassisml-sdk',
    zip_safe=False,
)
