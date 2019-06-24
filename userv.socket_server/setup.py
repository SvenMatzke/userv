from setuptools import setup
import sdist_upip

setup(
    name='userv.socket_server',
    version='0.3.0',
    packages=['userv'],
    url='https://github.com/SvenMatzke/userv',
    license='MIT',
    author='SvenMatzke',
    author_email='matzke.sven@googlemail.com',
    description='Async server for userv',
    long_description=open('README.rst').read(),
    cmdclass={'sdist': sdist_upip.sdist},
    install_requires=['userv>=0.4.0', 'micropython-ulogging']
)
