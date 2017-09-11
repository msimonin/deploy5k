# -*- coding: utf-8 -
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='deploy5k',
    version='0.0.3',
    description='',
    url='',
    author='msimonin',
    author_email='matthieu.simonin@inria.fr',
    license='GPL-3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        ],
    keywords='Evaluation, Reproducible Research, Grid5000',
    long_description=read('README.rst'),
    packages=find_packages(),
    install_requires=[
        'jsonschema >= 2.6.0, < 2.7',
        'execo >= 2.6.2, < 2.7',
        'requests>=2.18.0, <2.19'
    ],
    include_package_data=True
)
