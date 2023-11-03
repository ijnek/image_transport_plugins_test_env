from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node

from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    ld = LaunchDescription()

    this_package = FindPackageShare('image_transport_plugins_test_env')

    ld.add_action(IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('urdf_launch'), 'launch', 'display.launch.py']),
        launch_arguments={
            'urdf_package': 'image_transport_plugins_test_env',
            'urdf_package_path': PathJoinSubstitution(['urdf', 'cameras.urdf']),
            'jsp_gui': 'false',
            'rviz_config': PathJoinSubstitution([this_package, 'rviz', 'urdf.rviz'])}.items()
    ))

    # Gazebo
    ld.add_action(IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])),
        launch_arguments={
            'gz_args': [
                '-r ',  # Run simulation on start.
                PathJoinSubstitution([this_package, 'world', 'world.sdf']),
            ]
        }.items()
    ))

    # Create robot in Gazebo
    ld.add_action(Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-z', '0.1',
        ],
    ))

    # ROS <-> GZ Bridge
    ld.add_action(Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Clock (GZ -> ROS2)
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # RGB image
            '/rgb_camera@sensor_msgs/msg/Image[ignition.msgs.Image',
        ],
    ))

    return ld
