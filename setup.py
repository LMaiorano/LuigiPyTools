#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: setup
project: LuigiPyTools
date: 5/21/2020
author: lmaio
"""

from setuptools import setup

setup(
    name='LuigiPyTools',
    packages=['LuigiPyTools'],
    description='Tools commonly used in engineering projects',
    version='0.2.1',
    url='https://github.com/LMaiorano/LuigiPyTools',
    author='Luigi Maiorano',
    author_email='lmaiorano97@gmail.com',
    license='LICENSE.txt',
    long_description=open('README.md').read(),
    keywords=['pip', 'lmaiorano', 'pytools'],
    install_requires=[
        "google-api-python-client>=1.8.3",
        "google-auth-httplib2>=0.0.3",
        "google-auth-oauthlib>=0.4.1",
        "numpy>=1.18.4",
        "pandas>=1.0.3",
    ]
)
