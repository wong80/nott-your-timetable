"""Shared fixtures."""
from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def eee_report() -> str:
    """Real report for BEng EEE Year 2, academic year 2025/26.

    Captured from the timetabling server; week 1 starts on 1 Sep 2025.
    Staff names have been replaced with placeholders.
    """
    return (FIXTURES / "beng_eee_y2_2025.html").read_text(encoding="latin-1")
