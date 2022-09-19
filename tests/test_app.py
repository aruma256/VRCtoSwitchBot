from vrctoswitchbot import app


def test_to_str():
    assert app.to_str(1.234) == '1.23'
    assert app.to_str(1) == '1.00'
