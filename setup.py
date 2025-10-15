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
        # This is the new, more robust way to specify files.
        (os.path.join('share', package_name, 'launch'), [
            os.path.join('launch', 'boat_sim.launch.py')
        ]),
        (os.path.join('share', package_name, 'description'), [
            os.path.join('description', 'boat.urdf')
        ]),
        (os.path.join('share', package_name, 'rviz'), [
            os.path.join('rviz', 'boat_sim.rviz')
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
        ],
    },
)