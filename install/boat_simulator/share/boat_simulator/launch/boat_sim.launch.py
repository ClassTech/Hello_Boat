import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # --- Find all the necessary files ---
    urdf_file_path = os.path.join(
        get_package_share_directory('boat_simulator'), 'description', 'boat.urdf')

    rviz_config_file_path = os.path.join(
        get_package_share_directory('boat_simulator'), 'rviz', 'boat_sim.rviz')

    # Read the URDF file content
    with open(urdf_file_path, 'r') as file:
        robot_description_content = file.read()

    # --- Define all the nodes ---
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )

    simulator_node = Node(
        package='boat_simulator',
        executable='simulator',
        name='boat_simulator_node',
        output='screen'
    )

    teleop_node = Node(
        package='boat_simulator',
        executable='teleop',
        name='keyboard_teleop_node',
        output='screen',
        prefix='xterm -hold -e'
    )

    # --- This is the new RViz Node ---
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file_path] # Use '-d' to load our config file
    )

    # --- Return the full launch description ---
    return LaunchDescription([
        robot_state_publisher_node,
        simulator_node,
        teleop_node,
        rviz_node, # Add rviz to the launch
    ])