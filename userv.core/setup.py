from setuptools import setup
import sdist_upip

setup(
    name='userv',
    version='0.4.2',
    packages=['userv'],
    url='https://github.com/SvenMatzke/userv',
    license='MIT',
    author='SvenMatzke',
    author_email='matzke.sven@googlemail.com',
    description='Minimalistic core for webserver on microcontroler',
    long_description=open('README.rst').read(),
    cmdclass={'sdist': sdist_upip.sdist},
    install_requires=['ujson']
)
