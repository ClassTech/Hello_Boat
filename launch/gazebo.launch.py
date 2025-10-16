import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'boat_simulator'

    # Get the path to the Gazebo ROS package
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Get the path to your boat_simulator package
    pkg_boat_simulator = get_package_share_directory(package_name)

    # --- Gazebo Launch ---
    # This includes the standard Gazebo launch file, telling it to use our world file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': os.path.join(pkg_boat_simulator, 'worlds', 'gate.world')}.items()
    )

    # --- Robot State Publisher ---
    # Reads the URDF file and publishes the robot's state (TF transforms)
    urdf_file_path = os.path.join(pkg_boat_simulator, 'description', 'boat.urdf')
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': open(urdf_file_path).read()}]
    )

    # --- Spawn Entity ---
    # This node takes the robot description and "spawns" it into the Gazebo simulation
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'boat'],
        output='screen'
    )

    # --- Return the Launch Description ---
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
    ])