"""GOLDEN FIXTURE: two passing tests and one failing one."""


def test_addition():
    assert 1 + 1 == 2


def test_string_join():
    assert "-".join(["a", "b"]) == "a-b"


def test_deliberate_failure():
    assert 1 + 1 == 3, "deliberate: this fixture exists to produce a red"
