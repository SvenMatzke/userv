import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup
import os
sys.path.append("..")
import sdist_upip

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='userv',
    version='0.1.0',
    packages=[''],
    url='https://github.com/SvenMatzke/userv',
    license='MIT',
    author='SvenMatzke',
    author_email='matzke.sven@googlemail.com',
    description='minimal socket webserver for designed to work on esp8266',
    long_description=README,
    cmdclass={'sdist': sdist_upip.sdist},
    py_modules=['userv.py'],
)
