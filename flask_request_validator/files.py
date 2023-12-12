import mimetypes
import re
from typing import Iterable, Dict

from werkzeug.datastructures import FileStorage

from .exceptions import FilesLimitError, FileMimeTypeError, FileSizeError, FileNameError, FileMissingError


class File:
    def __init__(self, name: str, mime_types: Iterable, max_size: int) -> None:
        self._mime_types = mime_types
        self._max_size = max_size
        self._name = name

    def validate(self, files: Dict[str, FileStorage]):
        file = files.get(self._name)

        if not file:
            raise FileMissingError(self._name)
        if file.mimetype not in self._mime_types:
            raise FileMimeTypeError(file.name, file.mimetype, self._mime_types)

        file_length = len(file.read())
        if file_length > self._max_size:
            raise FileSizeError(file.name, file_length, self._max_size)


class FileChain:
    def __init__(self, mime_types: Iterable, max_size: int, max_files: int, name_pattern: str = '') -> None:
        self._name_pattern = name_pattern
        self._max_files = max_files
        self._mime_types = mime_types
        self._max_size = max_size

    def validate(self, files: Dict[str, FileStorage]) -> None:
        if len(files) > self._max_files:
            raise FilesLimitError(self._max_files)

        bad_names = []
        mime_types = mimetypes.types_map
        for name, file in files.items():
            if self._name_pattern:
                pattern = re.compile(self._name_pattern)
                file_name = file.filename
                for ext in mime_types.keys():
                    if file_name.endswith(ext):
                        file_name = file_name[0:file_name.rfind(ext)]
                        break

                if not pattern.match(file_name):
                    bad_names.append(file.filename)
                    continue

            File(name, self._mime_types, self._max_size).validate(files)

        if bad_names:
            raise FileNameError(bad_names, self._name_pattern)
