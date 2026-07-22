# pylint: disable=missing-function-docstring, missing-module-docstring
from unittest import mock

import pytest

from eq_cims_management_ui.utils.database.cir_operations import (
    make_authenticated_request,
)


@pytest.mark.usesfixture()
def test_make_authenticated_request():
    with mock.patch("google.oauth2.id_token.fetch_id_token"):
        response = make_authenticated_request(url="https://example.com")
        assert response.status_code == 200
