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
from flask import request
from flask_request_validator.request import FlaskRequest
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


app = flask.Flask(__name__)
app.request_class = FlaskRequest


@app.route('/<string:key>/<string:uuid>', methods=['POST'])
@validate_params(
    Param('key', VIEW, Type(str), Enum('key1', 'key2')),
    Param('uuid', VIEW, Type(str), Pattern(r'^[a-z-_.]{8,10}$')),
    Param('id', GET, Type(int)),
    Param('price', POST, Type(float), Required()),
)
def route(key, uuid):
    # example route: host/key1/qwertyuio?id=1
    print request.get_valid_param(POST, 'price')) # 2.01 (float)
    print request.get_valid_param(GET, 'id')) # 1 (int)
```

What are the VIEW, GET, POST params?
    VIEW param is an argument in the view function. See the example above.
    `key` and `uuid` are arguments for the route. They are stored in `request.view_args`.
    GET are params in the request string example: /my_route?f_name=test&l_name=tests2
    POST are params in `request.form`

Which types are supported?
    `str, bool, int, float, dict, list`

How to use `list` and `dict` params?

```
@app.route('/', methods=['POST'])
@validate_params(
    Param('id', POST, Type(list)), # should be sent as string `1,2,3`
    Param('query', POST, Type(dict)), # should be sent as string `key1:val1, key2,val2`
)
def route():
    print request.get_valid_param(POST, 'id')) # [1, 2, 3] (list)
    print request.get_valid_param(POST, 'query')) # {'key1': 'val1', 'key2': 'val2'} (dict)

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

Also you can create your custom rule. Here is a small example:

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
