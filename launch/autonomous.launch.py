import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'boat_simulator'
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_boat_simulator = get_package_share_directory(package_name)

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': os.path.join(pkg_boat_simulator, 'worlds', 'gate.world')}.items()
    )

    # Robot State Publisher
    urdf_file_path = os.path.join(pkg_boat_simulator, 'description', 'boat.urdf')
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': open(urdf_file_path).read()}]
    )

    # Spawn Entity
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'boat'],
        output='screen'
    )

    # Gate Detector Node
    detector_node = Node(
        package=package_name,
        executable='detector',
        name='gate_detector_node',
        output='screen'
    )

    # Gate Controller Node
    controller_node = Node(
        package=package_name,
        executable='controller',
        name='gate_controller_node',
        output='screen'
    )

    # --- THIS IS THE NEW NODE YOU ARE ADDING ---
    image_view_node = Node(
        package='rqt_gui',
        executable='rqt_gui',
        name='image_viewer',
        arguments=['--standalone', 'rqt_image_view'],
        remappings=[
            ('/image', '/my_camera/image_raw') # Remap the default topic to our camera
        ]
    )
    # ---------------------------------------------

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        detector_node,
        controller_node,
        image_view_node, # Add the new node to the launch list
    ])