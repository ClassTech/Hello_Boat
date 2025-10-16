import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from visualization_msgs.msg import Marker  # <--- THIS IS THE MISSING LINE
import math

class BoatSimulator(Node):
    """
    This node simulates the boat's movement and publishes its position for visualization.
    """
    def __init__(self):
        super().__init__('boat_simulator')
        
        self.subscription = self.create_subscription(
            Twist, 'cmd_vel', self.cmd_vel_callback, 10)
        self.odom_publisher = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.marker_publisher = self.create_publisher(Marker, 'visualization_marker', 10)

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.latest_twist = Twist()

        self.timer = self.create_timer(0.1, self.update_and_publish)
        self.get_logger().info('Boat Simulator Node has started.')

    def cmd_vel_callback(self, msg):
        self.latest_twist = msg

    def update_and_publish(self):
        dt = 0.1
        self.theta += self.latest_twist.angular.z * dt
        self.x += self.latest_twist.linear.x * dt * math.cos(self.theta)
        self.y += self.latest_twist.linear.x * dt * math.sin(self.theta)
        
        current_time = self.get_clock().now().to_msg()
        q_z = math.sin(self.theta / 2.0)
        q_w = math.cos(self.theta / 2.0)
        
        # --- Publish TF ---
        t = TransformStamped()
        t.header.stamp = current_time
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.rotation.z = q_z
        t.transform.rotation.w = q_w
        self.tf_broadcaster.sendTransform(t)

        # --- Publish Odometry ---
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_link'
        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.orientation.z = q_z
        odom_msg.pose.pose.orientation.w = q_w
        self.odom_publisher.publish(odom_msg)

        # --- Publish a simple cube Marker ---
        marker = Marker()
        marker.header.frame_id = "odom"
        marker.header.stamp = current_time
        marker.ns = "boat"
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.position.x = self.x
        marker.pose.position.y = self.y
        marker.pose.position.z = 0.0
        marker.pose.orientation.z = q_z
        marker.pose.orientation.w = q_w
        marker.scale.x = 1.0
        marker.scale.y = 0.5
        marker.scale.z = 0.3
        marker.color.a = 1.0 # Don't forget the alpha!
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        self.marker_publisher.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    node = BoatSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()