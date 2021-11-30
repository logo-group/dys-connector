from setuptools import setup, find_packages

VERSION = '0.1.0'
DESCRIPTION = 'Logo DYS Connector'
LONG_DESCRIPTION = 'Logo DYS(Doküman Yönetim Sistemi) API Python Implementation'

setup(
    name='dys-connector',
    version=VERSION,
    packages=find_packages(exclude=['tests*']),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    setup_requires=['wheel'],
    install_requires=['requests'],
    url='https://github.com/logo-group/dys-connector',
    author='Mustafa Talha Arslan, Furkan Arif Bozdağ',
    author_email='mustafa.arslan@logo.com.tr, arif.bozdag@logo.com.tr'
)