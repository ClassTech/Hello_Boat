import os
from glob import glob  # <-- CRITICAL: Add this import
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
        
        # This section now correctly finds all your asset files
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.py'))),
        (os.path.join('share', package_name, 'description'), glob(os.path.join('description', '*.urdf'))),
        (os.path.join('share', package_name, 'rviz'), glob(os.path.join('rviz', '*.rviz'))),
        (os.path.join('share', package_name, 'worlds'), glob(os.path.join('worlds', '*.world'))),
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
        'controller = boat_simulator.gate_controller_node:main', # <-- Add this line
    ],
},
)