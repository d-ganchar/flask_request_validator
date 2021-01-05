## Flask request validator

[![Build Status](https://api.travis-ci.org/d-ganchar/flask_request_validator.svg?branch=master)](https://travis-ci.org/d-ganchar/flask_request_validator)
[![Coverage Status](https://coveralls.io/repos/github/d-ganchar/flask_request_validator/badge.svg?branch=master)](https://coveralls.io/github/d-ganchar/flask_request_validator?branch=master)


Package provide possibility to validate of Flask request.

Key features
------------
- Easy and beautiful
- Type conversion
- Extensible
- Supports [Flask-RESTful](https://flask-restful.readthedocs.io/en/latest/)
- Supports Python 3.6 / 3.7 / 3.8 / 3.9
- Python 2.7 / 3.5 supported up to version 3.0

### How to install:

```
$ pip install flask_request_validator
```

### How to use:

**List of request parameters**:

`GET` - parameter stored in flask.request.args

`FORM` - parameter stored in flask.request.form

`JSON` - parameter stored in flask.request.get_json()

`PATH` - parameter stored in flask.request.view_args. In this case is part of route

`HEADER` - parameter stored header


**List of possible rules for validation**:

`Pattern(r'^[a-z-_.]{8,10}$')` - value checks at regexp. Works only for `str` values.

`MaxLength(6)` - value checks at max length. Works for `str` and `list` values.

`MinLength(6)` - value checks at min length. Works for `str` and `list` values.

`Max(6)` - checks that value is less or equal. Works for `int` and `float`.

`Min(6)` - checks that value is greater or equal. Works for `int` and `float`.

`Enum('value1', 'value2')` - describes allowed values

`NotEmpty` - checks that value is not empty. Works for `str` values and removes leading/trailing whitespace automatically.

`IsDatetimeIsoFormat` - checks that value is a `datetime` in ISO format and converts it to `datetime`.

`IsEmail` - checks that value is a valid email address.

`AbstractRule` - provide possibility to write custom rule

**Supported types for values**:

`str, bool, int, float, dict, list`

`bool` should be sent from client as: `1`, `0`, or `true` / `false` in any register

`list` should be sent from client as `value1,value2,value3`. 

`dict` should be sent from client as `key1:val1,key2:val2`. 

Here an example of route with validator:


```
from flask_request_validator import (
    PATH,
    FORM,
    Param,
    Pattern,
    validate_params
)


@app.route('/<string:uuid>', methods=['POST'])
@validate_params(
    Param('uuid', PATH, str, rules=[Pattern(r'^[a-z-_.]{8,10}$')]),
    Param('price', FORM, float),
)
def route(uuid, price):
    print uuid # str
    print price # float
```

Param description:

```
Param(
    name: the name of the request parameter
    param_type: where stored param(GET, FORM, JSON, PATH, HEADER)
    value_type: str, bool, int, float, dict, list - which type we want to have
    required: a bool that indicates wheter a value is required, True by default
    default: the default value, None by default. You can use lambda for this arg - default=lambda: ['test']
    rule: the list of rules (see class Rule)
)

```

One more example(request `/orders?finished=True&amount=100`):

```
@app.route('/orders', methods=['GET'])
@validate_params(
    Param('finished', GET, bool, required=False),
    Param('amount', GET, int, required=False),
)
def route(finished, amount):
    print finished # True (bool)
    print amount # 100 (int)

```

Also you can create your custom rule. Here is a small example:

```
from flask_request_validator import AbstractRule


def reserved_values():
    return ['today', 'tomorrow']


class MyRule(AbstractRule):

    def validate(self, value):
        errors = []
        if value in reserved_values():
            errors.append('Value %s is reserved' % value)

        # other errors...
        errors.append('One more error')

        return errors


@app.route('/')
@validate_params(
    Param('day', GET, str, False, rules=[MyRule()])
)
def hi(day):
    return day
```

Open `?day=today`. You will see the exception: 

```
InvalidRequest: Invalid request data. {"day": ["Value today is reserved", "One more error"]}
```

Also you can combine rules(`CompositeRule`) for frequent using:

```
from flask_request_validator import CompositeRule


name_rule = CompositeRule(Pattern(r'^[a-z-_.]{8,10}$'), one_more_rule, your_custom_rule, etc...)


@app.route('/person')
@validate_params(
    Param('first_name', GET, str, rules=name_rule),
    # other params is just example
    Param('streets', GET, list), should be sent as string `street1,stree2`
    Param('city', GET, str, rules=[Enum('Minsk')]),
    Param('meta', GET, dict), # should be sent as string `key1:val1,key2:val2`
)
def route_one(first_name, streets, city, meta):
    # print(first_name) (str)
    # print(streets) (list)
    # print(city) (str)
    # print(meta) (dict)
```
