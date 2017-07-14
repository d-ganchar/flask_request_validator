from setuptools import setup
from codecs import open
from os import path

current_path = path.abspath(path.dirname(__file__))

with open(path.join(current_path, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='flask_request_validator',
    version='2.0.1',
    description='Flask request data validation',
    long_description=long_description,
    url='https://github.com/d-ganchar/flask_request_validator',
    author='Danila Ganchar',
    author_email='danila.ganchar@gmail.com',
    license='MIT',
    keywords='flask request validation',
    packages=['flask_request_validator'],
    install_requires=['flask'],
    tests_require=['nose'],
)
