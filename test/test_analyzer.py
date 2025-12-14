from analyzer import is_protected


def test_protected_branch():
    assert is_protected("main") is True
    assert is_protected("feature-login") is False
