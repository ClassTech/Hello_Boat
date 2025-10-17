import os
import random
import math
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'boat_simulator'
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_boat_simulator = get_package_share_directory(package_name)

    # Calculate a random starting pose
    start_x = "-5.0"
    start_y = str(random.uniform(-3.0, 3.0))
    start_yaw = str(random.uniform(-math.pi / 2, math.pi / 2))

    # --- THIS IS THE CORRECTED ACTION ---
    # We wrap the pkill command in a shell script that always succeeds.
    kill_gazebo_cmd = ExecuteProcess(
        cmd=['bash', '-c', 'pkill -9 gz || true'],
        output='screen'
    )
    # ------------------------------------

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': os.path.join(pkg_boat_simulator, 'worlds', 'gate.world')}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': open(os.path.join(pkg_boat_simulator, 'description', 'boat.urdf')).read()}]
    )

    delayed_actions = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=['-topic', 'robot_description', '-entity', 'boat', '-x', start_x, '-y', start_y, '-Y', start_yaw],
                output='screen'
            ),
            Node(
                package=package_name,
                executable='detector',
                name='gate_detector_node',
                output='screen'
            ),
            Node(
                package=package_name,
                executable='controller',
                name='gate_controller_node',
                output='screen'
            ),
        ]
    )

    # Event handler to chain the actions sequentially
    run_gazebo_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=kill_gazebo_cmd,
            on_exit=[gazebo]
        )
    )

    return LaunchDescription([
        kill_gazebo_cmd,
        run_gazebo_handler,
        robot_state_publisher,
        delayed_actions,
    ])