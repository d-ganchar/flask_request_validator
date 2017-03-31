## Flask request validator

[![Build Status](https://api.travis-ci.org/d-ganchar/flask_request_validator.svg?branch=master)](https://travis-ci.org/d-ganchar/flask_request_validator)
[![Coverage Status](https://coveralls.io/github/d-ganchar/flask_request_validator/badge.svg?branch=master&service=github)](https://coveralls.io/github/d-ganchar/flask_request_validator?branch=master)


Extension provide posibility to validate of Flask request using @validate_params decorator.

### How to use:

```
from flask_request_validator import (
    Enum,
    GET,
    POST,
    Param,
    Type,
    Pattern,
    Required,
    validate_params
)

@app.route('/<string:key>/<string:uuid>', methods=['POST'])
@validate_params(
    Param('key', GET, Type(str), Enum('key1', 'key2')),
    Param('uuid', GET, Type(str), Pattern(r'^[a-z-_.]{8,10}$')),
    Param('sys', POST, Type(str), Required(), Pattern(r'^[a-z.]{3,6}$')),
    Param('type', POST, Type(str), Enum('type1', 'type2')),
)
def route(key, uuid):
   pass
```
