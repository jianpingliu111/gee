"""Unit tests for the heartbeat timeout threshold."""

import unittest

from swarm_heartbeat_monitor.heartbeat_timeout import is_heartbeat_timed_out


class TestHeartbeatTimeout(unittest.TestCase):
    """Check that a heartbeat outage only times out after three seconds."""

    TIMEOUT_NS = 3_000_000_000

    def test_does_not_trigger_at_exactly_three_seconds(self) -> None:
        self.assertFalse(
            is_heartbeat_timed_out(
                last_heartbeat_ns=1_000_000_000,
                now_ns=4_000_000_000,
                timeout_ns=self.TIMEOUT_NS,
            )
        )

    def test_triggers_after_more_than_three_seconds(self) -> None:
        self.assertTrue(
            is_heartbeat_timed_out(
                last_heartbeat_ns=1_000_000_000,
                now_ns=4_000_000_001,
                timeout_ns=self.TIMEOUT_NS,
            )
        )


if __name__ == "__main__":
    unittest.main()
