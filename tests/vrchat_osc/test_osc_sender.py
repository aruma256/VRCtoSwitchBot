from threading import Thread
from time import sleep
from unittest.mock import Mock
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

from vrctoswitchbot.vrchat_osc.osc_sender import OSCSender


def test___init__():
    sender = OSCSender('192.168.1.1', 9123)
    assert sender._client._address == '192.168.1.1'
    assert sender._client._port == 9123


def test_send():
    # setup Sender
    sender = OSCSender('127.0.0.1', 9123)
    # setup server
    callback_mock = Mock()
    dispatcher = Dispatcher()
    dispatcher.set_default_handler(callback_mock)
    server = osc_server.BlockingOSCUDPServer(('127.0.0.1', 9123), dispatcher)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    # test 1
    sender.send('/avatar/parameters/Light', True)
    sleep(0.1)
    callback_mock.assert_called_once_with('/avatar/parameters/Light', True)
    callback_mock.reset_mock()
    # test 2
    sender.send('/avatar/parameters/Fan', False)
    sleep(0.1)
    callback_mock.assert_called_once_with('/avatar/parameters/Fan', False)
    # shutdown
    server.shutdown()
    thread.join(timeout=0.1)
