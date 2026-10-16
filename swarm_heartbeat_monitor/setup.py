from setuptools import find_packages, setup

package_name = 'swarm_heartbeat_monitor'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jianpingliu111',
    maintainer_email='jianpingliu111@example.com',
    description='Monitors MAVROS heartbeat and triggers a swarm failsafe when no heartbeat is received for more than 3 seconds.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'heartbeat_node = swarm_heartbeat_monitor.heartbeat_node:main',
        ],
    },
)
