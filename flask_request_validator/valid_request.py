from abc import ABC, abstractmethod
from typing import Any

from flask import Request


class ValidRequest(ABC):
    @abstractmethod
    def get_form(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_headers(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_json(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_params(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_path_params(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_flask_request(self) -> Request:
        pass
