from setuptools import setup
import sdist_upip

setup(
    name='userv.async_server',
    version='0.3.4',
    packages=['userv'],
    url='https://github.com/SvenMatzke/userv',
    license='MIT',
    author='SvenMatzke',
    author_email='matzke.sven@googlemail.com',
    description='Async server for userv',
    long_description=open('README.rst').read(),
    cmdclass={'sdist': sdist_upip.sdist},
    install_requires=['micropython-uasyncio', 'userv', 'micropython-ulogging']
)
