import io
from setuptools import setup
from os import path

current_path = path.abspath(path.dirname(__file__))

with io.open("README.rst", "rt", encoding="utf8") as f:
    long_description = f.read()

setup(
    name='flask_request_validator',
    version='2.1.2',
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
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Flask',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
