import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np

class GateDetectorNode(Node):
    def __init__(self):
        super().__init__('gate_detector_node')
        self.bridge = CvBridge()
        
        self.subscription = self.create_subscription(
    Image,
    '/my_camera/image_raw',  # <-- The correct topic!
    self.image_callback,
    10)
        
        self.publisher = self.create_publisher(Point, '/gate/target_pixel', 10)

        # --- NEW: Publisher for the debug image ---
        self.debug_publisher = self.create_publisher(Image, '/gate/debug_mask', 10)
        
        self.get_logger().info('Gate Detector Node has started.')

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            return

        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # These values might need tuning for the specific red in Gazebo
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv_image, lower_red, upper_red)

        # --- NEW: Publish the mask for debugging ---
        # We must convert the single-channel mask back to a ROS Image message
        self.debug_publisher.publish(self.bridge.cv2_to_imgmsg(mask, "mono8"))

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) >= 2:
            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            pole1_contour = sorted_contours[0]
            pole2_contour = sorted_contours[1]

            M1 = cv2.moments(pole1_contour)
            if M1["m00"] != 0:
                cx1 = int(M1["m10"] / M1["m00"])
                cy1 = int(M1["m01"] / M1["m00"])
            else: return

            M2 = cv2.moments(pole2_contour)
            if M2["m00"] != 0:
                cx2 = int(M2["m10"] / M2["m00"])
                cy2 = int(M2["m01"] / M2["m00"])
            else: return
            
            midpoint_x = (cx1 + cx2) / 2.0
            midpoint_y = (cy1 + cy2) / 2.0

            target_point = Point()
            target_point.x = midpoint_x
            target_point.y = midpoint_y
            target_point.z = 0.0
            self.publisher.publish(target_point)

def main(args=None):
    rclpy.init(args=args)
    node = GateDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()