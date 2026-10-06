"""Regression tests for the A4 master-document synchronization gate."""
from tools.verify_a4_docs import verify


def test_a4_master_documentation_is_synchronized() -> None:
    """A stale status surface must fail the test suite instead of becoming silent debt."""
    assert verify() == []
