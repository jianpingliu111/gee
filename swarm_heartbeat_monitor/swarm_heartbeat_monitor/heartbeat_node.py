"""ROS 2 node that monitors the MAVROS state heartbeat."""

import rclpy
from mavros_msgs.msg import State
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from std_msgs.msg import Bool

from .heartbeat_timeout import is_heartbeat_timed_out


HEARTBEAT_TIMEOUT_SECONDS = 3.0
CHECK_PERIOD_SECONDS = 0.1
NANOSECONDS_PER_SECOND = 1_000_000_000


class HeartbeatMonitorNode(Node):
    """Publish a failsafe trigger when MAVROS state messages go stale."""

    def __init__(self) -> None:
        super().__init__("heartbeat_monitor")

        self._heartbeat_timeout_ns = int(
            HEARTBEAT_TIMEOUT_SECONDS * NANOSECONDS_PER_SECOND
        )
        # A steady clock makes the failsafe independent of simulated ROS time.
        self._steady_clock = Clock(clock_type=ClockType.STEADY_TIME)
        # Start the watchdog at node startup so a missing first heartbeat also
        # triggers the failsafe after the timeout window.
        self._last_heartbeat_ns = self._steady_clock.now().nanoseconds
        self._failsafe_published_for_current_outage = False

        self._failsafe_publisher = self.create_publisher(
            Bool,
            "/swarm/failsafe_trigger",
            10,
        )
        self._state_subscription = self.create_subscription(
            State,
            "/mavros/state",
            self._on_state,
            10,
        )
        self._timeout_timer = self.create_timer(
            CHECK_PERIOD_SECONDS,
            self._check_heartbeat_timeout,
            clock=self._steady_clock,
        )

        self.get_logger().info(
            "Monitoring /mavros/state; timeout is "
            f"{HEARTBEAT_TIMEOUT_SECONDS:.1f} seconds."
        )

    def _on_state(self, _message: State) -> None:
        """Record the time at which a MAVROS state message was received."""
        self._last_heartbeat_ns = self._steady_clock.now().nanoseconds
        # A new heartbeat marks recovery and permits a trigger for a later outage.
        self._failsafe_published_for_current_outage = False

    def _check_heartbeat_timeout(self) -> None:
        """Publish one True trigger when the current heartbeat becomes stale."""
        now_ns = self._steady_clock.now().nanoseconds
        if self._failsafe_published_for_current_outage:
            return

        if is_heartbeat_timed_out(
            last_heartbeat_ns=self._last_heartbeat_ns,
            now_ns=now_ns,
            timeout_ns=self._heartbeat_timeout_ns,
        ):
            message = Bool()
            message.data = True
            self._failsafe_publisher.publish(message)
            self._failsafe_published_for_current_outage = True
            self.get_logger().error(
                "No /mavros/state heartbeat received for more than "
                f"{HEARTBEAT_TIMEOUT_SECONDS:.1f} seconds; published "
                "True on /swarm/failsafe_trigger."
            )


def main(args=None) -> None:
    """Run the heartbeat monitor node."""
    rclpy.init(args=args)
    node = HeartbeatMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
