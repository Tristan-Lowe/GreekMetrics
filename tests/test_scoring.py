# tests/test_scoring.py
import pytest
from scoring import compute_score, score_hex


def test_compute_score_all_tens():
    c, e, m, total = compute_score([10]*5, [10]*5, [10]*5)
    assert c == 10.0
    assert e == 10.0
    assert m == 10.0
    assert total == 100.0


def test_compute_score_all_ones():
    c, e, m, total = compute_score([1]*5, [1]*5, [1]*5)
    assert c == 1.0
    assert e == 1.0
    assert m == 1.0
    assert total == 10.0


def test_compute_score_mixed():
    c, e, m, total = compute_score([6]*5, [8]*5, [7]*5)
    assert c == 6.0
    assert e == 8.0
    assert m == 7.0
    assert total == 70.1


def test_compute_score_returns_rounded():
    c, e, m, total = compute_score([7, 8, 6, 9, 7], [5, 6, 7, 8, 4], [9, 8, 7, 6, 5])
    assert isinstance(c, float)
    assert len(str(c).split('.')[-1]) <= 2


def test_score_hex_green():
    assert score_hex(80) == '#4ade80'
    assert score_hex(95) == '#4ade80'
    assert score_hex(100) == '#4ade80'


def test_score_hex_yellow():
    assert score_hex(65) == '#facc15'
    assert score_hex(79) == '#facc15'


def test_score_hex_red():
    assert score_hex(64) == '#f87171'
    assert score_hex(10) == '#f87171'
