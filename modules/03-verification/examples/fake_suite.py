#!/usr/bin/env python3
r"""EXAMPLE GATE PAYLOAD - delete this and point the gate at your real suite.

It exists so a fresh adopter can watch verify.py go green, red, and partial
within a minute of cloning, without owning a project yet.

The shape is what to copy, not the content:

  * ONE summary line, machine-greppable, with the count IN it:
        example_unit: 4/4 cases passed
    Both numbers, so `(\d+)/\1` can assert "all of them" rather than
    "some of them".
  * a distinct FAILURE line the veto pattern can match, so a red run is red
    for a stated reason rather than by absence.
  * an honesty suffix when the run was a SUBSET:
        example_unit: 4/4 cases passed (subset: 4 of 40)
    The gate's veto pattern matches `(subset:` - a partial run may not
    certify, and the payload is what makes that detectable.

    --fail    print the failure shape
    --subset  print the honesty suffix
    --shrink  print a well-formed line with a smaller count (floor breach)
"""
import sys

args = sys.argv[1:]
CASES = ["parses an empty document", "rejects a duplicate id",
         "round-trips unicode", "reports the line number on a syntax error"]

if "--fail" in args:
    for c in CASES[:3]:
        print(f"  [PASS] {c}")
    print(f"  [FAIL] {CASES[3]}")
    print("example_unit: THESE FAILED: reports the line number on a syntax error")
    print("example_unit: 3/4 cases passed")
    sys.exit(1)

n = 2 if "--shrink" in args else len(CASES)
for c in CASES[:n]:
    print(f"  [PASS] {c}")
suffix = " (subset: 4 of 40)" if "--subset" in args else ""
print(f"example_unit: {n}/{n} cases passed{suffix}")
