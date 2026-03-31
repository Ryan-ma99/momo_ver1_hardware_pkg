cmake_minimum_required(VERSION 3.8)
project(momo_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(control_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED) # 추가: 파이썬 GUI에서 사용
find_package(std_srvs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(PkgConfig REQUIRED)

# yaml-cpp 라이브러리 찾기
pkg_check_modules(YAML_CPP REQUIRED yaml-cpp)

# 의존성 목록
set(dependencies
  rclcpp
  std_msgs
  sensor_msgs
  geometry_msgs
  control_msgs
  trajectory_msgs # 추가
  std_srvs
  visualization_msgs
  ament_index_cpp
)

install(PROGRAMS
  scripts/momo_control_gui.py
  DESTINATION lib/${PROJECT_NAME}
)

# launch, config 디렉토리가 있다면 설치
install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
  OPTIONAL
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()