#!/usr/bin/env python3
"""EXAMPLE GATE PAYLOAD - delete this and point the gate at your real linter.

Demonstrates three things the unit-suite example does not:

  * a COMPONENT line (`rule set v1`) that the gate asserts separately via
    require_also. A summary that passes without its component step is a
    summary that certifies nothing - it is how a suite reports green after
    silently loading zero rules.
  * a CEILING: 1 WARN is ratified, a second is news. Ceilings stop a project
    absorbing warnings one at a time until nobody reads them.
  * a FAIL count inside the required line itself, so a lint with failures
    cannot match the pattern at all.

    --warn   emit a second, unratified warning (ceiling breach)
    --fail   emit failures
    --norules  drop the component line (the silent-zero-rules shape)
"""
import sys

args = sys.argv[1:]
if "--norules" not in args:
    print("example_lint: rule set v1")

warns = 2 if "--warn" in args else 1
fails = 3 if "--fail" in args else 0
checks = 12
oks = checks - warns - fails

print("  WARN  line-length near the limit in examples/fake_suite.py")
if warns > 1:
    print("  WARN  an unratified second warning nobody has looked at yet")
if fails:
    print("  FAIL  a rule that is actually broken")
print(f"example_lint: {checks} checks, {fails} FAIL, {warns} WARN, {oks} OK")
sys.exit(1 if fails else 0)
