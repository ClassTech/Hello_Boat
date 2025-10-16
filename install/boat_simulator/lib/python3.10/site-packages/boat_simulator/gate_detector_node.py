import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np

class GateDetectorNode(Node):
    """
    This node subscribes to a camera feed, detects two red poles,
    and publishes the pixel coordinates of the midpoint between them.
    """
    def __init__(self):
        super().__init__('gate_detector_node')
        self.bridge = CvBridge()

        # Subscribe to the camera image topic from Gazebo
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)

        # Publish the detected gate's center point
        self.publisher = self.create_publisher(Point, '/gate/target_pixel', 10)

        self.get_logger().info('Gate Detector Node has started.')

    def image_callback(self, msg):
        try:
            # Convert the ROS Image message to an OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            return

        # --- OpenCV Perception Pipeline ---

        # 1. Convert from BGR to HSV color space (better for color filtering)
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # 2. Define the range for the color red and create a mask
        #    These values might need tuning depending on the lighting in Gazebo
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv_image, lower_red, upper_red)

        # 3. Find contours (shapes) in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) >= 2:
            # 4. Sort contours by area and get the two largest ones
            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            pole1_contour = sorted_contours[0]
            pole2_contour = sorted_contours[1]

            # 5. Calculate the center (centroid) of each pole
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

            # 6. Calculate the midpoint between the two poles
            midpoint_x = (cx1 + cx2) / 2.0
            midpoint_y = (cy1 + cy2) / 2.0

            # 7. Create and publish the Point message
            target_point = Point()
            target_point.x = midpoint_x
            target_point.y = midpoint_y
            target_point.z = 0.0  # z is not used in 2D
            self.publisher.publish(target_point)

            # Optional: Log the detected point for debugging
            # self.get_logger().info(f'Gate detected at: ({midpoint_x:.2f}, {midpoint_y:.2f})')


def main(args=None):
    rclpy.init(args=args)
    node = GateDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()