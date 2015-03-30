#!/usr/bin/env python
# Copyright (c) 2015 Adam Drakeford <adam.drakeford@gmail.com>
# See LICENSE for more details

"""
Distutils installer for txGraylog.
"""

from setuptools import setup, find_packages

setup(
    name='txGraylog',
    version='1.0',
    description='A twisted log service that interacts with Graylog2.',
    author='Adam Drakeford',
    author_email='adamdrakeford@gmail.com',
    license='MIT',
    packages=find_packages(),
    tests_require=['twisted>=10.2.0', 'coverage', 'jsonlib'],
    install_requires=['twisted>=10.2.0', 'jsonlib'],
    requires=['twisted(>=10.2.0)'],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Development Status :: 3 - Alpha',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: MIT License (MIT)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
