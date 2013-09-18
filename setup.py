# from setuptools import setup
# import os.path

import os
import sys

from distutils.core import setup

setup(
    name = 'humanapi',
    version = '0.1.0',
    author = 'Ola Wiberg',
    author_email = 'ola@humanapi.co',
    description = 'A CLI client and Python API library for the HumanAPI health data platform.',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    license = 'MIT',
    keywords = 'humanapi sensor data',
    url = 'https://github.org/humanapi/humanapi-python-client/',
    install_requires = ['requests >= 0.13.2', 'docopt == 0.4.0'],
    classifiers = [
        'Development Status :: 1 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Health :: Data'
    ]
)
