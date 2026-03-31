# momo_ver1_hardware_pkg
이 패키지는 momo_ver1 을 가동시키기 위한 패키지 입니다.
위 패키지를 [workspace]/src 에 설치

설치방법
1. dynamixel_hardware_interface 설치
설치시 [workspace]/src 위치에 설치

https://github.com/ROBOTIS-GIT/dynamixel_hardware_interface

2. U2D2 설정
왼팔,오른팔,머리 u2d2 의 시리얼 번호를 알기 위해 터미널에 아래 코드 기입 (여러개를 꼽았으면 ttyUSB0 ,ttyUSB1, ttyUSB2 시도)
~~~
udevadm info -a -n /dev/ttyUSB0 | grep '{serial}'
~~~
아래와 같은 시리얼 번호가 나오는데 위에 시리얼 코드를 기억
~~~
ATTRS{serial}=="FTAK8CAO"
ATTRS{serial}=="0000:0a:00.0"
~~~

아래의 코드로 규칙파일 생성
~~~
sudo nano /etc/udev/rules.d/99-u2d2.rules
~~~
규칙 파일에 아래 코드를 기입하고 각 U2D2에 맞는 시리얼 번호 기입 (아래 시리얼 코드는 임의)
~~~
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", ATTRS{serial}=="FTAK8CAO", SYMLINK+="left_arm_u2d2"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", ATTRS{serial}=="FTAK8D74", SYMLINK+="right_arm_u2d2"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", ATTRS{serial}=="FTAK8A96", SYMLINK+="head_u2d2"

ACTION=="add", SUBSYSTEM=="usb-serial", DRIVER=="ftdi_sio", ATTR{latency_timer}="1"
~~~
규칙 적용
~~~
sudo udevadm control --reload-rules
sudo udevadm trigger
~~~
연결된 U2D2 분리후 다시 꼽고 확인
~~~
ls -l /dev/left_arm_u2d2
ls -l /dev/right_arm_u2d2
ls -l /dev/head_arm_u2d2 
~~~
3.패키지 설치
ros2_control, move_it 설치
~~~
sudo apt install ros-humble-ros2-control
sudo apt install ros-humble-moveit
~~~
[workspace] 에서 
~~~
colcon build
source install/setup.bash
~~~
4. Test
ros2_control 실행
~~~
ros2 launch momo_pkg momo_robot_ros_control.launch.py
~~~
간단한 joint publisher gui 실행
~~~
ros2 run momo_pkg momo_control_gui.py 
~~~

