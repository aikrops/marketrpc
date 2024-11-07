import marketrpc
from setuptools import setup, find_packages

setup(
    name='python-marketrpc',
    version='0.0.1',
    author='aikrops',
    author_email='aikrops@tradingx.io',
    description='marketrpc',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://www.tradingx.io',
    packages=find_packages(),
    install_requires=[
        "grpcio==1.67.1",
        "grpcio-tools==1.67.1",
        "protobuf==5.28.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)