from unittest import mock

import pytest

from eq_cims_management_ui.utils.database.cir_operations import make_authenticated_request


def test_get_cir_metadata():
    pass


def test_check_cir_status():
    pass


@pytest.mark.usesfixture()
def test_make_authenticated_request():
    with mock.patch("google.oauth2.id_token.fetch_id_token"):
        response = make_authenticated_request(url="https://example.com")
        assert response.status_code == 200
