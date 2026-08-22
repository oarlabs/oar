"""GOLDEN FIXTURE: three passing tests and two deliberate skips.

The skips are unconditional so the fixture reports the same counts on every
host. A real suite's skips are usually conditional, which is exactly why the
adapter checks the skip COUNT rather than trusting it."""
import pytest


def test_addition():
    assert 1 + 1 == 2


def test_string_join():
    assert "-".join(["a", "b"]) == "a-b"


def test_sorted_is_stable():
    assert sorted([3, 1, 2]) == [1, 2, 3]


@pytest.mark.skip(reason="deliberate: stands in for a platform-gated test")
def test_platform_gated():
    raise AssertionError("never reached")


@pytest.mark.skip(reason="deliberate: stands in for a network-gated test")
def test_network_gated():
    raise AssertionError("never reached")
