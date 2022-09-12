from setuptools import setup, find_packages
import pathlib

VERSION = '0.2.8'
DESCRIPTION = 'Logo DYS Connector API Python Implementation'

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='dys-connector',
    version=VERSION,
    packages=find_packages(exclude=['tests*']),
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    setup_requires=['wheel'],
    install_requires=['requests'],
    url='https://github.com/logo-group/dys-connector',
    author='Mustafa Talha Arslan, Furkan Arif Bozdag, Hilal Ozkan',
    author_email='mustafa.arslan@logo.com.tr, arif.bozdag@logo.com.tr, hilal.ozkan@logo.com.tr'
)