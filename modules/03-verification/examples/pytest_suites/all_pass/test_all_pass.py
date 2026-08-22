"""GOLDEN FIXTURE: the ordinary green. Three tests, all passing."""


def test_addition():
    assert 1 + 1 == 2


def test_string_join():
    assert "-".join(["a", "b"]) == "a-b"


def test_sorted_is_stable():
    assert sorted([3, 1, 2]) == [1, 2, 3]
