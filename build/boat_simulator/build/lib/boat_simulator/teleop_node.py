import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import tty
import termios
import sys

class KeyboardTeleop(Node):
    """ This node reads keyboard input and publishes it as velocity commands. """
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.get_logger().info('Keyboard Teleop Node Started.')
        self.print_instructions()
        self.run_loop()

    def get_key(self):
        """ Function to get a single key press from the terminal. """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def print_instructions(self):
        """ Prints the instructions for the user. """
        self.get_logger().info('--- Reading from keyboard ---')
        self.get_logger().info('        w/s : move forward/backward')
        self.get_logger().info('        a/d : turn left/right')
        self.get_logger().info('  any other key to stop')
        self.get_logger().info('        q   : quit')
        self.get_logger().info('---------------------------')

    def run_loop(self):
        """ Main loop to read keys and publish commands. """
        while rclpy.ok():
            key = self.get_key()
            twist = Twist() # Create a new, zeroed-out message

            if key == 'w':
                twist.linear.x = 0.5  # Move forward
            elif key == 's':
                twist.linear.x = -0.5 # Move backward
            elif key == 'a':
                twist.angular.z = 1.0 # Turn left
            elif key == 'd':
                twist.angular.z = -1.0 # Turn right

            # Publish the command. If no key was matched, it publishes a zero Twist message, stopping the boat.
            self.publisher_.publish(twist)

            if key.lower() == 'q':
                self.get_logger().info('Quitting teleop node.')
                break

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()
    # The run_loop is blocking, so we don't need to spin
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()