from setuptools import find_packages, setup

package_name = "swarm_heartbeat_monitor"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Swarm Heartbeat Monitor Maintainers",
    maintainer_email="maintainers@example.com",
    description=(
        "Monitor MAVROS state heartbeats and publish a swarm failsafe "
        "trigger on timeout."
    ),
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "heartbeat_node = swarm_heartbeat_monitor.heartbeat_node:main",
        ],
    },
)
