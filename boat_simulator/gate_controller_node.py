import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from geometry_msgs.msg import Point, Twist
import math
from abc import ABC, abstractmethod

class StateEnum:
    SEARCHING = 1
    APPROACHING = 2
    PASS_THROUGH = 3
    FINISHED = 4

class State(ABC):
    def __init__(self, controller_node, state_enum):
        self.node = controller_node
        self.state_enum = state_enum
    @abstractmethod
    def execute(self):
        pass

class SearchingState(State):
    def execute(self):
        twist_msg = Twist()
        twist_msg.angular.z = 0.3
        self.node.publisher.publish(twist_msg)

class ApproachingState(State):
    def execute(self):
        if not self.node.has_fresh_target():
            self.node.transition_to_state(self.node.passthrough_state)
            return
        target_x = self.node.last_target_msg.x
        error = self.node.image_center - target_x
        gain = 0.002
        angular_velocity = gain * error
        twist_msg = Twist()
        twist_msg.linear.x = self.node.FORWARD_SPEED_MPS
        twist_msg.angular.z = angular_velocity
        self.node.publisher.publish(twist_msg)

class PassThroughState(State):
    def __init__(self, controller_node, state_enum):
        super().__init__(controller_node, state_enum)
        self.drive_timer_start_time = None
    def execute(self):
        if self.drive_timer_start_time is None:
            distance = (self.node.GATE_WIDTH_METERS / 2.0) / math.tan(self.node.CAMERA_FOV_RADIANS / 2.0)
            self.drive_timer_duration = (distance / self.node.FORWARD_SPEED_MPS) + 1.5
            self.drive_timer_start_time = self.node.get_clock().now()
            self.node.get_logger().warn(f'State: PASS_THROUGH. Driving straight for {self.drive_timer_duration:.2f}s.')
        time_since_start = (self.node.get_clock().now() - self.drive_timer_start_time).nanoseconds / 1e9
        if time_since_start < self.drive_timer_duration:
            twist_msg = Twist()
            twist_msg.linear.x = self.node.FORWARD_SPEED_MPS
            self.node.publisher.publish(twist_msg)
        else:
            self.drive_timer_start_time = None
            self.node.transition_to_state(self.node.finished_state)

class FinishedState(State):
    def execute(self):
        self.node.publisher.publish(Twist())
        if not self.node.timer.is_canceled():
            self.node.get_logger().info('Mission complete. Stopping controller timer.')
            self.node.timer.cancel()

class GateControllerNode(Node):
    def __init__(self):
        super().__init__('gate_controller_node')
        self.subscription = self.create_subscription(Point, '/gate/target_pixel', self.target_callback, 10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.declare_parameter('image_width', 800)
        self.image_width = self.get_parameter('image_width').get_parameter_value().integer_value
        self.image_center = self.image_width / 2.0
        self.FORWARD_SPEED_MPS = 0.6
        self.CAMERA_FOV_RADIANS = 1.8
        self.GATE_WIDTH_METERS = 2.0
        self.last_target_msg = None
        self.last_msg_time = self.get_clock().now()
        self.target_lost_timeout = 1.0
        self.searching_state = SearchingState(self, StateEnum.SEARCHING)
        self.approaching_state = ApproachingState(self, StateEnum.APPROACHING)
        self.passthrough_state = PassThroughState(self, StateEnum.PASS_THROUGH)
        self.finished_state = FinishedState(self, StateEnum.FINISHED)
        self.state = self.searching_state
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info(f'Controller started. Entering {type(self.state).__name__}')

    def target_callback(self, msg):
        self.last_target_msg = msg
        self.last_msg_time = self.get_clock().now()
        if self.state.state_enum == StateEnum.SEARCHING and self.has_fresh_target():
            self.transition_to_state(self.approaching_state)

    def has_fresh_target(self):
        time_since_last = (self.get_clock().now() - self.last_msg_time).nanoseconds / 1e9
        return time_since_last < self.target_lost_timeout

    def transition_to_state(self, new_state):
        if self.state.state_enum != new_state.state_enum:
            self.get_logger().info(f'Leaving {type(self.state).__name__}, Entering {type(new_state).__name__}')
            self.state = new_state

    def control_loop(self):
        if self.state:
            self.state.execute()

def main(args=None):
    rclpy.init(args=args)
    node = GateControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()