#!/usr/bin/env python

from setuptools import setup, find_namespace_packages


INSTALL_REQUIRES = [
    'pymongo==3.11.2',
]

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='mongo-transport',
    version='0.1',
    description='Message transport queue running on a MongoDB backend',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
    url='https://github.com/pkpinto/mongo-transport',
    author='Paulo Kauscher Pinto',
    author_email='paulo.kauscher.pinto@icloud.com',
    license='Apache License 2.0',
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    install_requires=INSTALL_REQUIRES,
)
