#!/usr/bin/env python

from os.path import join, dirname

from setuptools import setup


def read(filename):
    with open(join(dirname(__file__), filename)) as fileobj:
        return fileobj.read()


MODULE = 'rundeck_create_users_from_ldap'
COMMAND = MODULE.replace('_', '-')
VERSION = [line for line in read('%s.py' % MODULE).splitlines()
           if line.startswith('VERSION = ')][0].split("'")[1]


setup(
    name=COMMAND,
    version=VERSION,
    description='Create Rundeck users from LDAP.',
    long_description=read('README.rst'),
    license='Apache License 2.0',
    url='https://github.com/pmuller/%s' % COMMAND,
    author='Philippe Muller',
    author_email='philippe.muller@gmail.com',
    py_modules=[MODULE],
    entry_points="""
        [console_scripts]
        %s = %s:main
    """ % (COMMAND, MODULE),
    install_requires=[
        'JayDeBeApi >= 1.0.0',
        'python-ldap >= 2.4.29',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
    ],
)
