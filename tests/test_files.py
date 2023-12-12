import io
from unittest import TestCase

import flask
from flask_restful import Api
from parameterized import parameterized

from flask_request_validator import *


_app = flask.Flask(__name__)
_test_api = Api(_app, '/v1')

_app.testing = True

_app2 = flask.Flask(__name__)


@_app2.errorhandler(RequestError)
def handler(e):
    return str(e.files), 400


@_app2.route('/issue/85', methods=['POST'])
@validate_params(
    File(
        mime_types=['application/pdf'],
        max_size=22,
        name='document',
    ),
    File(
        mime_types=['image/jpeg'],
        max_size=22,
        name='photo',
    )
)
def issue_85(valid: ValidRequest):
    return str(valid.get_flask_request().files.keys())


@_app2.route('/issue/85-chain', methods=['POST'])
@validate_params(
    FileChain(
        mime_types=['application/pdf', 'image/jpeg'],
        max_size=22,
        max_files=2,
        name_pattern='^[a-z]+$',
    )
)
def issue_85_chain(valid: ValidRequest):
    return str(valid.get_flask_request().files.keys())


class TestFiles(TestCase):
    def test_wrong_usage(self):
        with self.assertRaises(WrongUsageError):
            @validate_params(
                FileChain(
                    mime_types=['application/pdf', 'image/jpeg'],
                    max_size=1024,
                    max_files=3,
                ),
                File('test', ['test'], 27),
            )
            def route(request: ValidRequest):
                pass

    @parameterized.expand([
        (
            dict(),
            b"[FileMissingError('document'), FileMissingError('photo')]",
        ),
        (
            dict(photo=(io.BytesIO(b'very long photo content'), 'photo.jpg')),
            b"[FileMissingError('document'), FileSizeError('photo', 23, 22)]",
        ),
        (
            dict(document=(io.BytesIO(b'very long document content'), 'document.pdf')),
            b"[FileSizeError('document', 26, 22), FileMissingError('photo')]",
        ),
        (
            dict(
                document=(io.BytesIO(b'very long document content'), 'document.pdf'),
                photo=(io.BytesIO(b'very long photo content'), 'photo.jpg'),
            ),
            b"[FileSizeError('document', 26, 22), FileSizeError('photo', 23, 22)]",
        ),
        (
            dict(
                document=(io.BytesIO(b'good pdf'), 'document.pdf'),
                photo=(io.BytesIO(b'good jpg'), 'photo.jpg'),
            ),
            b"dict_keys(['document', 'photo'])",
        ),
    ])
    def test_issue_85(self, data: dict, expected: bytes):
        with _app2.test_client() as client:
            response = client.post(
                '/issue/85',
                data=data,
                follow_redirects=True,
                content_type='multipart/form-data',
            )

            self.assertEqual(response.data, expected)

    @parameterized.expand([
        (
            dict(
                document=(io.BytesIO(b'very long document content'), 'document.pdf'),
                photo=(io.BytesIO(b'very long photo content'), 'photo.jpg'),
            ),
            b"[FileSizeError('document', 26, 22)]",
        ),
        (
            dict(
                document=(io.BytesIO(b'bad pdf'), 'd0cumeNT.pdf'),
                photo=(io.BytesIO(b'bad jpg'), 'ph0T0.jpg'),
            ),
            b"[FileNameError(['d0cumeNT.pdf', 'ph0T0.jpg'], '^[a-z]+$')]",
        ),
        (
            dict(
                document=(io.BytesIO(b'good pdf'), 'document.pdf'),
                photo=(io.BytesIO(b'good jpg'), 'photo.jpg'),
                pic=(io.BytesIO(b'files limit'), 'pic.jpg'),
            ),
            b"[FilesLimitError(2)]",
        ),
        (
            dict(
                document=(io.BytesIO(b'good pdf'), 'document.pdf'),
                photo=(io.BytesIO(b'good jpg'), 'photo.jpg'),
            ),
            b"dict_keys(['document', 'photo'])",
        ),
    ])
    def test_issue_85_chain(self, data: dict, expected: bytes):
        with _app2.test_client() as client:
            response = client.post(
                '/issue/85-chain',
                data=data,
                follow_redirects=True,
                content_type='multipart/form-data',
            )

            self.assertEqual(response.data, expected)
