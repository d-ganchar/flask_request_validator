## Flask request validator

[![Build Status](https://api.travis-ci.org/d-ganchar/flask_request_validator.svg?branch=master)](https://travis-ci.org/d-ganchar/flask_request_validator)
[![Coverage Status](https://coveralls.io/repos/github/d-ganchar/flask_request_validator/badge.svg?branch=master)](https://coveralls.io/github/d-ganchar/flask_request_validator?branch=master)


Package provide possibility to validate of Flask request and convert parameters to specific type.

### How to install:

```
$ pip install flask_request_validator
```

### How to use:

**There are 4 types of request parameters**:

`GET` - parameter stored in flask.request.args

`FORM` - parameter stored in flask.request.form

`JSON` - parameter stored in flask.request.get_json()

`PATH` - parameter stored in flask.request.view_args. In this case is part of route


**Here a list of possible rules for validation**:

`Pattern(r'^[a-z-_.]{8,10}$')` - value checks at regexp. Works only for `str` values.

`MaxLength(6)` - value checks at max length. Works for `str` and `list` values.

`MixLength(6)` - value checks at min length. Works for `str` and `list` values.

`Enum('value1', 'value2')` - describes allowed values

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
    param_name_in_request, # str
    request_param_type, # where stored param(GET, FORM, JSON, PATH)
    type_of_value, # str, bool, int, float, dict, list - which type we want to have
    required_or_no, bool - True by default
    default_value, None by default. You can use lambda for this arg - default=lambda: ['test']
    list_of_rules
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


You can combine rules(`CompositeRule`) for frequent using:

```
from flask_request_validator import CompositeRule


name_rule = CompositeRule(Pattern(r'^[a-z-_.]{8,10}$'), your_custom_rule...)


@app.route('/person', methods=['POST'])
@validate_params(
    Param('first_name', JSON, str, rules=name_rule),
    # other params is just example
    Param('streets', JSON, list), should be sent as string `street1,stree2`
    Param('city', JSON, str, rules=[Enum('Minsk')]),
    Param('meta', JSON, dict), # should be sent as string `key1:val1, key2,val2`
)
def route_one(first_name, streets, city, meta):
    # first_name (str)
    # streets (list)
    # city (str)
    # meta (dict)
```

Also you can create your custom rule. Here is a small example:

```
from flask_request_validator import AbstractRule


class MyRule(AbstractRule):

    def validate(self, value):
        errors = []
        # do something ...
        errors.append('My error')
        return errors
```
