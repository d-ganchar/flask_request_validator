## Flask request validator

[![Build Status](https://api.travis-ci.org/d-ganchar/flask_request_validator.svg?branch=master)](https://travis-ci.org/d-ganchar/flask_request_validator)
[![Coverage Status](https://coveralls.io/repos/github/d-ganchar/flask_request_validator/badge.svg?branch=master)](https://coveralls.io/github/d-ganchar/flask_request_validator?branch=master)


Extension provide possibility to validate of Flask request using `@validate_params` decorator.

### How to install:

```
$ pip install flask_request_validator
```

### How to use:

```
from flask_request_validator import (
    Enum,
    GET,
    VIEW,
    POST,
    Param,
    Type,
    Pattern,
    Required,
    validate_params
)

@app.route('/<string:key>/<string:uuid>', methods=['POST'])
@validate_params(
    Param('key', VIEW, Type(str), Enum('key1', 'key2')),
    Param('uuid', VIEW, Type(str), Pattern(r'^[a-z-_.]{8,10}$')),
    Param('id', GET, Type(int)),
    Param('sys', POST, Type(str), Required(), Pattern(r'^[a-z.]{3,6}$')),
    Param('type', POST, Type(str), Enum('type1', 'type2')),
)
def route(key, uuid):
```

You can combine rules for frequent using `CompositeRule`:

```
from flask_request_validator import CompositeRule

type_rule = CompositeRule(Required(), Enum('type1', 'type2'))


@app.route('/route_one', methods=['POST'])
@validate_params(
    Param('type', POST, type_rule),
    # other params
)
def route_one():
    pass

@app.route('/route_two', methods=['POST'])
@validate_params(
    Param('type', POST, type_rule),
    # other params
)
def route_two():
```

Also you can create your custom rule. Here a small example:

```
from flask_request_validator.rules import AbstractRule

class MyRule(AbstractRule):

    def validate(self, value):
        return ['Value "%s" is not valid' % value]

@app.route('/route_one', methods=['POST'])
@validate_params(
    Param('type', POST, MyRule())
)
def route_one():
```
