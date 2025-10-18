import os
import random
import math
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction, RegisterEventHandler, SetEnvironmentVariable
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'boat_simulator'
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_boat_simulator = get_package_share_directory(package_name)

    set_ros_distro = SetEnvironmentVariable(name='ROS_DISTRO', value='humble')

    start_x = "-5.0"
    start_y = str(random.uniform(-3.0, 3.0))
    start_yaw = str(random.uniform(math.pi / 2, 3 * math.pi / 2))

    urdf_file_path = os.path.join(pkg_boat_simulator, 'description', 'boat.urdf')
    with open(urdf_file_path, 'r') as file:
        robot_description_content = file.read()

    kill_gazebo_cmd = ExecuteProcess(
        cmd=['bash', '-c', 'pkill -9 gz || true'],
        output='screen'
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': os.path.join(pkg_boat_simulator, 'worlds', 'gate.world'),
            'extra_gazebo_args': 'OGRE_RENDER_SYSTEM=GL'
        }.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}]
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'boat', '-x', start_x, '-y', start_y, '-Y', start_yaw],
        output='screen'
    )

    detector_node = Node(
        package='boat_simulator',
        executable='detector',
        name='gate_detector_node',
        output='screen'
    )

    controller_node = Node(
        package='boat_simulator',
        executable='controller',
        name='gate_controller_node',
        output='screen'
    )

    image_view_node = Node(
        package='rqt_gui',
        executable='rqt_gui',
        name='image_viewer',
        arguments=['--standalone', 'rqt_image_view'],
        remappings=[('/image', '/my_camera/image_raw')]
    )

    run_gazebo_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=kill_gazebo_cmd,
            on_exit=[gazebo, robot_state_publisher]
        )
    )

    delayed_autonomy_handler = TimerAction(
        period=5.0,
        actions=[spawn_entity, detector_node, controller_node, image_view_node]
    )

    return LaunchDescription([
        set_ros_distro,
        kill_gazebo_cmd,
        run_gazebo_handler,
        delayed_autonomy_handler,
    ])