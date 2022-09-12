from unittest.mock import Mock, patch

from vrctoswitchbot import version_checker


def _create_dummy_response(status_code: int, recommended: str = '') -> Mock:
    response_mock = Mock()
    response_mock.status_code = status_code
    response_mock.json.return_value = {'recommended': recommended}
    return response_mock


@patch('requests.get')
def test_is_newer_version_available(mocked_get):
    f = version_checker.is_newer_version_available
    mocked_get.return_value = _create_dummy_response(200, recommended='1.0.1')
    assert f('1.0.0') is True
    mocked_get.return_value = _create_dummy_response(200, recommended='1.0.0')
    assert f('1.0.0') is False
    mocked_get.return_value = _create_dummy_response(404)
    assert f('1.0.0') is False
    mocked_get.side_effect = RuntimeError
    assert f('1.0.0') is False


def test__is_local_version_outdated():
    f = version_checker._is_local_version_outdated
    assert f(remote_version='1.0.0', local_version='1.0.0') is False
    assert f(remote_version='1.0.1', local_version='1.0.0') is True
