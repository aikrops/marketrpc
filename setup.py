from setuptools import setup, find_packages

setup(
    name='marketrpc',
    version='0.0.1',
    author='aikrops',
    author_email='aikrops@tradingx.io',
    description='marketrpc api',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/aikrops/marketrpc',
    packages=find_packages(),
    install_requires=[
        "grpcio",
        "grpcio-tools"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)