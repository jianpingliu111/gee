"""Heartbeat monitor node for a swarm of MAVROS-connected vehicles.

The node subscribes to ``/mavros/state`` and records the timestamp of the
last received heartbeat. If no new heartbeat arrives within
:data:`HEARTBEAT_TIMEOUT_SEC` seconds, it publishes ``True`` on
``/swarm/failsafe_trigger`` so that the swarm can react to a lost link.
"""

import time

HEARTBEAT_TIMEOUT_SEC = 3.0
CHECK_PERIOD_SEC = 0.5

try:
    import rclpy
    from rclpy.node import Node
    from mavros_msgs.msg import State
    from std_msgs.msg import Bool

    _ROS_AVAILABLE = True
except Exception:  # pragma: no cover - allows importing logic without ROS
    rclpy = None
    Node = object
    State = None
    Bool = None
    _ROS_AVAILABLE = False


class HeartbeatMonitor:
    """Pure, ROS-independent heartbeat timeout logic.

    Tracks the timestamp of the last received heartbeat and reports whether
    the configured timeout has elapsed since then.
    """

    def __init__(self, timeout_sec=HEARTBEAT_TIMEOUT_SEC):
        self.timeout_sec = float(timeout_sec)
        self.last_heartbeat = None

    def record_heartbeat(self, now=None):
        """Record that a heartbeat was received.

        ``now`` may be injected (e.g. for tests); otherwise the monotonic
        clock is used.
        """
        if now is None:
            now = time.monotonic()
        self.last_heartbeat = now

    def is_timed_out(self, now=None):
        """Return ``True`` when no heartbeat has been received for longer
        than ``timeout_sec`` seconds."""
        if self.last_heartbeat is None:
            return False
        if now is None:
            now = time.monotonic()
        return (now - self.last_heartbeat) > self.timeout_sec

    def reset(self):
        self.last_heartbeat = None


if _ROS_AVAILABLE:

    class HeartbeatNode(Node):
        """ROS2 node wrapping :class:`HeartbeatMonitor`."""

        def __init__(self, node_name='heartbeat_node'):
            super().__init__(node_name)
            self.monitor = HeartbeatMonitor(HEARTBEAT_TIMEOUT_SEC)
            self._failsafe_pub = self.create_publisher(
                Bool, '/swarm/failsafe_trigger', 10)
            self._state_sub = self.create_subscription(
                State, '/mavros/state', self._state_callback, 10)
            self._timer = self.create_timer(CHECK_PERIOD_SEC, self._check_timeout)
            self.get_logger().info('Heartbeat monitor started.')

        def _state_callback(self, msg):
            # mavros_msgs/State carries connected/armed flags; any message
            # counts as a heartbeat.
            self.monitor.record_heartbeat()
            self.get_logger().debug('Heartbeat received.')

        def _check_timeout(self):
            if self.monitor.is_timed_out():
                out = Bool()
                out.data = True
                self._failsafe_pub.publish(out)
                self.get_logger().warn(
                    'No heartbeat for more than %.1f s; failsafe triggered.'
                    % HEARTBEAT_TIMEOUT_SEC)

    def main(args=None):
        rclpy.init(args=args)
        node = HeartbeatNode()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()


else:  # pragma: no cover

    def main(args=None):
        raise RuntimeError('rclpy is not available; cannot run heartbeat_node')


if __name__ == '__main__':
    main()
