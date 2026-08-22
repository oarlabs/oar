"""GOLDEN FIXTURE: THE SILENT-GREEN CLASS. This module defines no tests.

pytest collects nothing here and prints `no tests ran`. A suite can arrive in
this state by accident - a renamed directory, a broken conftest, a changed
testpaths setting - and the point of the fixture is that a gate pointed
straight at pytest cannot tell this from a healthy run, while the adapter's
line must never be green over it."""


def helper_not_a_test():
    return 1
