import time

import pytest

from swarm_heartbeat_monitor.heartbeat_node import (
    HEARTBEAT_TIMEOUT_SEC,
    HeartbeatMonitor,
)


def test_no_timeout_before_threshold():
    monitor = HeartbeatMonitor(timeout_sec=3.0)
    monitor.record_heartbeat(now=0.0)
    assert monitor.is_timed_out(now=2.9) is False


def test_timeout_triggers_after_threshold():
    monitor = HeartbeatMonitor(timeout_sec=3.0)
    monitor.record_heartbeat(now=0.0)
    assert monitor.is_timed_out(now=3.1) is True


def test_no_heartbeat_never_reports_timeout():
    monitor = HeartbeatMonitor(timeout_sec=3.0)
    assert monitor.is_timed_out(now=10.0) is False


def test_heartbeat_resets_timeout():
    monitor = HeartbeatMonitor(timeout_sec=3.0)
    monitor.record_heartbeat(now=0.0)
    assert monitor.is_timed_out(now=4.0) is True
    monitor.record_heartbeat(now=4.0)
    assert monitor.is_timed_out(now=5.0) is False


def test_default_timeout_matches_spec():
    assert HEARTBEAT_TIMEOUT_SEC == 3.0
