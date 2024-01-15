from setuptools import setup

DESCRIPTION = """Flask Request Validator
=======================

See `readme`_

.. _readme: https://github.com/d-ganchar/flask_request_validator#flask-request-validator
"""

setup(
    name='flask_request_validator',
    version='4.4.0',
    description='Flask request data validation',
    long_description=DESCRIPTION,
    url='https://github.com/d-ganchar/flask_request_validator',
    author='Danila Ganchar',
    author_email='danila.ganchar@gmail.com',
    license='MIT',
    keywords='flask request validation',
    packages=['flask_request_validator'],
    install_requires=['flask'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Flask',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
