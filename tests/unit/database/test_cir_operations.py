# pylint: disable=missing-function-docstring, missing-module-docstring
from unittest import mock

from eq_cims_management_ui.utils.database.cir_operations import (
    make_authenticated_request,
)


@mock.patch("google.oauth2.id_token.fetch_id_token")
@mock.patch("requests.get", return_value=mock.Mock(status_code=200))
def test_make_authenticated_request(_mock_get, _mock_fetch_id_token):
    response = make_authenticated_request(url="https://example.com")
    assert response.status_code == 200
