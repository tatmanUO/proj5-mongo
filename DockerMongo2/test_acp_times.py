
"""
Tests for ACP brevet opening and closing times.
"""

from acp_times import open_time, close_time

START = "2026-11-08T10:00:00-08:00"


def check_times(distance, brevet, expected_open, expected_close):
    assert open_time(distance, brevet, START) == expected_open
    assert close_time(distance, brevet, START) == expected_close


def test_start_control():
    check_times(0, 200,
                "2026-11-08T10:00:00-08:00",
                "2026-11-08T11:00:00-08:00")


def test_early_control_20km():
    check_times(20, 200,
                "2026-11-08T10:35:00-08:00",
                "2026-11-08T12:00:00-08:00")


def test_early_control_59km():
    check_times(59, 200,
                "2026-11-08T11:44:00-08:00",
                "2026-11-08T13:57:00-08:00")


def test_early_control_60km():
    check_times(60, 200,
                "2026-11-08T11:46:00-08:00",
                "2026-11-08T14:00:00-08:00")


def test_early_control_61km():
    check_times(61, 200,
                "2026-11-08T11:48:00-08:00",
                "2026-11-08T14:04:00-08:00")


def test_100km_control():
    check_times(100, 300,
                "2026-11-08T12:56:00-08:00",
                "2026-11-08T16:40:00-08:00")


def test_before_200km_boundary():
    check_times(199, 200,
                "2026-11-08T15:51:00-08:00",
                "2026-11-08T23:16:00-08:00")


def test_200km_finish():
    check_times(200, 200,
                "2026-11-08T15:53:00-08:00",
                "2026-11-08T23:30:00-08:00")


def test_exceeds_200km_brevet():
    check_times(205, 200,
                "2026-11-08T15:53:00-08:00",
                "2026-11-08T23:30:00-08:00")


def test_after_200km_speed_boundary():
    check_times(201, 300,
                "2026-11-08T15:55:00-08:00",
                "2026-11-08T23:24:00-08:00")


def test_300km_finish():
    check_times(300, 300,
                "2026-11-08T19:00:00-08:00",
                "2026-11-09T06:00:00-08:00")


def test_400km_finish():
    check_times(400, 400,
                "2026-11-08T22:08:00-08:00",
                "2026-11-09T13:00:00-08:00")


def test_after_400km_speed_boundary():
    check_times(401, 600,
                "2026-11-08T22:10:00-08:00",
                "2026-11-09T12:44:00-08:00")


def test_600km_finish():
    check_times(600, 600,
                "2026-11-09T04:48:00-08:00",
                "2026-11-10T02:00:00-08:00")


def test_1000km_finish():
    check_times(1000, 1000,
                "2026-11-09T19:05:00-08:00",
                "2026-11-11T13:00:00-08:00")
