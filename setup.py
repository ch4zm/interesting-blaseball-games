from setuptools import setup, find_packages
import glob
import os

with open('requirements.txt') as f:
    required = [x for x in f.read().splitlines() if not x.startswith("#")]

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'Readme.md'), encoding='utf-8') as f:
    long_description = f.read()

# Note: the _program variable is set in __init__.py.
# it determines the name of the package/final command line tool.
from cli import __version__, _program

setup(
    name=_program,
    version=__version__,
    packages=['cli'],
    package_data = {
      'cli': ['data/*.json']
    },
    description='interesting-blaseball-games, a command line interface for finding interesting blaseball games',
    url='https://github.com/ch4zm/interesting-blaseball-games',
    author='Ch4zm of Hellmouth',
    author_email='ch4zm.of.hellmouth@gmail.com',
    license='MIT',
    entry_points="""
    [console_scripts]
    {program} = cli.command:main
    """.format(program = _program),
    install_requires=required,
    keywords=[],
    zip_safe=False,
    long_description=long_description,
    long_description_content_type='text/markdown'
)

