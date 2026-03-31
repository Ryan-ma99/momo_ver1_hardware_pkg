import os
import yaml
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
import xacro

def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)

    try:
        with open(absolute_file_path, "r") as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None

def generate_launch_description():
    # 패키지 경로와 설정 파일들
    current_pkg = "momo_pkg"
    momo_robot_description_pkg = "momo_robot_description"
    
    pkg_path = get_package_share_directory(current_pkg)
    momo_robot_description_pkg_path=get_package_share_directory(momo_robot_description_pkg)
    
    # URDF/XACRO 파일 로드 및 처리
    xacro_file = os.path.join(momo_robot_description_pkg_path, "urdf", "momo_robot.urdf.xacro")
    doc = xacro.process_file(xacro_file)
    robot_description = {"robot_description": doc.toxml()}
    
    # Controllers 설정 파일
    ros2_controllers_path = os.path.join(pkg_path, "config", "ros2_controllers.yaml")
    
    # RViz 설정 파일
    rviz_config_path = os.path.join(pkg_path, "config", "momo.rviz")
    
    
    # 노드 정의
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[robot_description]
    )
    
    # RViz2 노드
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config_path],
        output="screen"
    )
    
    # ros2_control 노드
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            ros2_controllers_path
        ],
        output="screen"
    )
    
    # 컨트롤러 스포너들
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager-timeout",
            "300",
            "--controller-manager",
            "/controller_manager",
        ]
    )
    
    left_arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_arm_controller", "-c", "/controller_manager"]
    )
    
    right_arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["right_arm_controller", "-c", "/controller_manager"]
    )
    
    head_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["head_controller", "-c", "/controller_manager"]
    )
   
    return LaunchDescription([
        robot_state_publisher,
        rviz_node,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        left_arm_controller_spawner,
        right_arm_controller_spawner,
        head_controller_spawner
    ])
