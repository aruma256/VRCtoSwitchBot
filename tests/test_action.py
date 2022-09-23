from unittest.mock import Mock
import pytest

from vrctoswitchbot.action import Action


def test_is_acceptable():
    a = Action(None, '/avatar/parameters/Light', None, None)
    # accepts the same address
    assert a.is_acceptable('/avatar/parameters/Light') is True
    assert a.is_acceptable('/avatar/parameters/Fan') is False


def test_on_osc():
    controller_mock = Mock()
    device_mock = Mock()
    device_mock.get_id.return_value = 'abc123'
    a = Action(controller_mock, '/avatar/parameters/Light', device_mock, 'turnOn')
    a.execute = Mock()
    f = a.on_osc
    # raises if value is not bool
    with pytest.raises(RuntimeError):
        f('/avatar/parameters/Light', 1)
    a.execute.assert_not_called()
    # ignores if value is False
    f('/avatar/parameters/Light', False)
    a.execute.assert_not_called()
    # calls execute if address matches and value is True
    f('/avatar/parameters/Light', True)
    a.execute.assert_called_once_with()


def test_execute():
    app_mock = Mock()
    app_mock.get_switchbot_controller.return_value = controller_mock = Mock()
    app_mock.get_osc_sender.return_value = osc_sender_mock = Mock()
    device_mock = Mock()
    device_mock.get_id.return_value = 'abc123'
    a = Action(app_mock, '/avatar/parameters/Light', device_mock, 'turnOn')
    # test 1
    a.execute()
    controller_mock.send_device_command.assert_called_once_with(
        device_id='abc123',
        command='turnOn',
    )
    osc_sender_mock.send.assert_called_once_with(
        '/avatar/parameters/Light',
        False,
    )
    controller_mock.reset_mock()
    osc_sender_mock.reset_mock()
    # test 2 (Exception)
    controller_mock.send_device_command.side_effect = Exception
    a.execute()
    osc_sender_mock.send.assert_called_once_with(
        '/avatar/parameters/Light',
        False,
    )
