import os
from setuptools import find_packages, setup

package_name = 'boat_simulator'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # --- EXPLICIT FILE PATHS ---
        # This is the most robust, non-magic way to specify every file.

        (os.path.join('share', package_name, 'launch'), [
            'launch/autonomous.launch.py',
            'launch/boat_sim.launch.py',
            'launch/gazebo.launch.py'
        ]),
        (os.path.join('share', package_name, 'description'), [
            'description/boat.urdf'
        ]),
        (os.path.join('share', package_name, 'rviz'), [
            'rviz/boat_sim.rviz'
        ]),
        (os.path.join('share', package_name, 'worlds'), [
            'worlds/gate.world'
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='parallels',
    maintainer_email='parallels@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simulator = boat_simulator.boat_sim_node:main',
            'teleop = boat_simulator.teleop_node:main',
            'detector = boat_simulator.gate_detector_node:main',
            'controller = boat_simulator.gate_controller_node:main',
        ],
    },
)