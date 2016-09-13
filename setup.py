from setuptools import setup, find_packages

from redux.version import __version__

packages = find_packages(exclude=['test', 'test.*'])

setup(
    name='redux',
    version=__version__,
    packages=packages,
)
