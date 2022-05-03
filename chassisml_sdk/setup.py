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
    python_requires='>=3.6,<3.9',
    install_requires=['requests','mlflow==1.22','numpy==1.19.5','pyyaml','validators','grpc-requests==0.1.0','grpcio>=1.44.0','docker==5.0.3',
                    'opencv-python-headless==4.5.4.60','onnxruntime==1.8.1','onnx==1.7.0','mxnet==1.8','boto3','xgboost==1.4','gluoncv==0.10.5','azureml-core>=1.41.0',
                    'azureml-automl-runtime==1.41.0','pandas==1.1.5'],
    url='https://github.com/modzy/chassis/tree/main/chassisml-sdk',
    zip_safe=False,
)
