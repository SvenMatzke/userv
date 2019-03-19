from setuptools import setup
import sdist_upip
import os
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='userv',
    version='0.1.0',
    packages=['userv'],
    url='https://github.com/SvenMatzke/userv',
    license='MIT',
    author='SvenMatzke',
    author_email='matzke.sven@googlemail.com',
    description='Minimal webserver for micropython Designed to work on esp8266 for socketserving and async for esp32',
    long_description=README,
    cmdclass={'sdist': sdist_upip.sdist},
    install_requires=['ujson', 'micropython-ulogging']
)
