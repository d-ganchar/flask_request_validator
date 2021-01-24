from abc import abstractmethod, ABC
from typing import Dict, Any


class ValidRequest(ABC):
    @abstractmethod
    def get_form(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_json(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_path_params(self) -> Dict[str, Any]:
        pass
