from abc import ABC, abstractmethod

from .valid_request import ValidRequest


class AbstractAfterParam(ABC):
    """
    :see: https://github.com/d-ganchar/flask_request_validator/issues/64
    """
    @abstractmethod
    def validate(self, value: ValidRequest):
        """
        Called when all structures are valid and types are converted
        (HEADERS, GET, POST has no errors)
        :raises AfterParamError:
        """
        pass
