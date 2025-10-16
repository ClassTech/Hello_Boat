import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Twist
import math

class GateControllerNode(Node):
    """
    A smarter controller that calculates its distance from the gate and
    drives for a calculated duration after losing sight of the target.
    """
    def __init__(self):
        super().__init__('gate_controller_node')
        
        # --- Node Setup ---
        self.subscription = self.create_subscription(
            Point, '/gate/target_pixel', self.target_callback, 10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # --- Parameters ---
        self.declare_parameter('image_width', 800)
        self.image_width = self.get_parameter('image_width').get_parameter_value().integer_value
        self.image_center = self.image_width / 2.0
        
        # --- Known constants for our simulation ---
        self.CAMERA_FOV_RADIANS = 1.8  # Must match the FOV in the boat.urdf
        self.GATE_WIDTH_METERS = 2.0   # Must match the pole separation in the gate.world
        self.FORWARD_SPEED_MPS = 0.6   # Meters per second, must match our desired speed

        # --- State and Memory ---
        self.last_twist_command = Twist()
        self.last_msg_time = self.get_clock().now()
        self.drive_timer_duration = 0.0  # How long we should continue driving for
        self.drive_timer_start_time = None
        
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info('Smarter Gate Controller Node has started.')

    def target_callback(self, msg):
        """When we see the target, update our steering command."""
        target_x = msg.x
        
        # Proportional Control Logic
        error = self.image_center - target_x
        gain = 0.002 
        angular_velocity = gain * error
        
        # Update the command in our "memory"
        self.last_twist_command.linear.x = self.FORWARD_SPEED_MPS
        self.last_twist_command.angular.z = angular_velocity
        
        # Update the timestamp
        self.last_msg_time = self.get_clock().now()
        
        self.get_logger().info(f'Target seen! Steering: {angular_velocity:.2f}')
        
        # Since we see the target, reset the drive-through timer
        self.drive_timer_start_time = None

    def control_loop(self):
        """
        The main logic loop. Decides what command to send based on whether
        we see the gate or are in the "drive-through" phase.
        """
        time_since_last_msg = (self.get_clock().now() - self.last_msg_time).nanoseconds / 1e9

        # --- Phase 1: We can see the gate ---
        # If our vision data is fresh, use the calculated steering command.
        if time_since_last_msg < 0.5:
            self.publisher.publish(self.last_twist_command)

        # --- Phase 2: We just lost the gate, start the "drive-through" timer ---
        elif self.drive_timer_start_time is None:
            # This is the moment we lose the poles from the sides of the FOV.
            # Calculate distance using trigonometry.
            distance_to_gate = (self.GATE_WIDTH_METERS / 2.0) / math.tan(self.CAMERA_FOV_RADIANS / 2.0)
            
            # Calculate the time needed to travel that distance plus a little extra.
            self.drive_timer_duration = (distance_to_gate / self.FORWARD_SPEED_MPS) + 1.0 # 1s buffer
            self.drive_timer_start_time = self.get_clock().now()
            
            self.get_logger().warn(f'Target lost! Calculated distance: {distance_to_gate:.2f}m. Driving for {self.drive_timer_duration:.2f}s.')
            
            # Continue with the last good command (go straight)
            self.last_twist_command.angular.z = 0.0 # Ensure we go straight
            self.publisher.publish(self.last_twist_command)

        # --- Phase 3: We are in the "drive-through" phase ---
        else:
            time_since_timer_start = (self.get_clock().now() - self.drive_timer_start_time).nanoseconds / 1e9
            if time_since_timer_start < self.drive_timer_duration:
                # Continue driving straight
                self.get_logger().info(f'Driving through gate... {time_since_timer_start:.1f}s / {self.drive_timer_duration:.1f}s')
                self.publisher.publish(self.last_twist_command)
            # --- Phase 4: Drive-through is complete, stop. ---
            else:
                self.get_logger().info('Drive-through complete. Stopping.')
                self.publisher.publish(Twist()) # Publish a zero Twist to stop

def main(args=None):
    rclpy.init(args=args)
    node = GateControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()