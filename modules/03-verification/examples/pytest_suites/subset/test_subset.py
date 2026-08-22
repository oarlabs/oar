"""GOLDEN FIXTURE: four tests, run with `-k parser` so two are DESELECTED.

A subset run is not a certification. The adapter prints the honesty suffix and
the gate's veto pattern matches it."""


def test_parser_reads_an_empty_document():
    assert True


def test_parser_reports_a_line_number():
    assert True


def test_writer_round_trips_unicode():
    assert True


def test_writer_rejects_a_duplicate_id():
    assert True
