from vrctoswitchbot import gui


def test_to_str():
    assert gui.to_str(1.234) == '1.23'
    assert gui.to_str(1) == '1.00'
