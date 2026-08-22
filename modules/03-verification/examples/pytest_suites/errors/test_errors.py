"""GOLDEN FIXTURE: two passing tests and one that ERRORS in setup.

An error is not a failure. A test whose fixture raises never ran, so a runner
that folds errors into the failure count loses the distinction between 'this
assertion is wrong' and 'this test could not start'."""
import pytest


def test_addition():
    assert 1 + 1 == 2


def test_string_join():
    assert "-".join(["a", "b"]) == "a-b"


@pytest.fixture
def broken_fixture():
    raise RuntimeError("deliberate: this fixture exists to produce an ERROR")


def test_needs_a_broken_fixture(broken_fixture):
    raise AssertionError("never reached")
