"""Pure heartbeat timeout logic, kept independent of ROS for easy testing."""


def is_heartbeat_timed_out(
    last_heartbeat_ns: int,
    now_ns: int,
    timeout_ns: int,
) -> bool:
    """Return whether the elapsed time is strictly greater than the timeout.

    Args:
        last_heartbeat_ns: Monotonic timestamp of the most recent heartbeat.
        now_ns: Current monotonic timestamp.
        timeout_ns: Timeout duration in nanoseconds.

    """
    return now_ns - last_heartbeat_ns > timeout_ns
