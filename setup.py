#!/usr/bin/env python
# Copyright (c) 2015 Adam Drakeford <adam.drakeford@gmail.com>
# See LICENSE for more details

"""
Distutils installer for txGraylog.
"""

from setuptools import setup, find_packages

setup(
    name='txGraylog',
    version='0.3',
    description='A twisted log service that interacts with Graylog2.',
    long_description=(
        'txGraylog is a a twisted based client that interacts with a '
        'Graylog server. Currently it supports the following protocols '
        'UDP and TCP protocols.'),
    author='Adam Drakeford',
    author_email='adamdrakeford@gmail.com',
    license='MIT',
    url='https://github.com/dr4ke616/txGraylog/',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    tests_require=['twisted>=10.2.0', 'coverage', 'jsonlib'],
    install_requires=['twisted>=10.2.0', 'jsonlib'],
    requires=['twisted(>=10.2.0)'],
    zip_safe=False,
    classifiers=[
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Logging',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
