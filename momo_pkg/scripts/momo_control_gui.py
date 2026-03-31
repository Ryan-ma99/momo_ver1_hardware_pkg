#!/usr/bin/env python3
import sys
import threading
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
import tkinter as tk
from tkinter import ttk

class JointControlGUI(Node):
    def __init__(self):
        super().__init__('joint_control_gui')
        
        # 컨트롤러별 조인트 이름 정의
        self.controllers = {
            'left_arm_controller': [f'left_arm_joint{i}' for i in range(1, 7)],
            'right_arm_controller': [f'right_arm_joint{i}' for i in range(1, 7)],
            'head_controller': ['head_yaw_joint', 'head_pitch_joint']
        }

        # 모든 조인트 목록 추출
        self.all_joints = [j for joints in self.controllers.values() for j in joints]
        self.joint_values = {joint: 0.0 for joint in self.all_joints}
        self.got_initial_state = False

        # 퍼블리셔 및 서브스크라이버 설정
        self.pubs = {name: self.create_publisher(JointTrajectory, f'/{name}/joint_trajectory', 10) 
                     for name in self.controllers.keys()}
        
        # 현재 상태를 받아오기 위한 서브스크라이버
        self.sub = self.create_subscription(JointState, '/joint_states', self.joint_state_callback, 10)

        self.get_logger().info("로봇의 현재 각도를 기다리는 중...")

    def joint_state_callback(self, msg):
        # 처음 한 번만 실행하거나, 현재 값을 계속 업데이트할 때 사용
        if not self.got_initial_state:
            for i, name in enumerate(msg.name):
                if name in self.joint_values:
                    self.joint_values[name] = msg.position[i]
            
            # 모든 조인트의 값을 찾았는지 확인 (필수 조인트가 다 포함되었는지)
            if all(j in msg.name for j in self.all_joints):
                self.got_initial_state = True
                self.get_logger().info("초기 위치 동기화 완료!")

    def create_widgets(self):
        self.root = tk.Tk()
        self.root.title("Momo Robot Joint Controller (Synced)")
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        row_idx = 0
        for group, joints in self.controllers.items():
            ttk.Label(main_frame, text=f"--- {group} ---", font=('Helvetica', 10, 'bold')).grid(row=row_idx, column=0, columnspan=2, pady=(10, 5))
            row_idx += 1
            
            for joint in joints:
                ttk.Label(main_frame, text=joint).grid(row=row_idx, column=0, sticky=tk.W)
                
                # 초기값을 현재 조인트 값(self.joint_values[joint])으로 설정
                initial_val = self.joint_values[joint]
                
                scale = ttk.Scale(main_frame, from_=-3.14, to=3.14, orient=tk.HORIZONTAL, length=250,
                                  command=lambda val, j=joint, g=group: self.update_joint(g, j, val))
                scale.set(initial_val) # <--- 여기가 핵심: 현재 값으로 슬라이더 초기화
                scale.grid(row=row_idx, column=1, sticky=(tk.W, tk.E))
                row_idx += 1

    def update_joint(self, group, joint, val):
        self.joint_values[joint] = float(val)
        self.publish_trajectory(group)

    def publish_trajectory(self, group):
        msg = JointTrajectory()
        msg.joint_names = self.controllers[group]
        point = JointTrajectoryPoint()
        point.positions = [self.joint_values[j] for j in msg.joint_names]
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = 50000000 # 0.05초 (반응성 향상)
        msg.points.append(point)
        self.pubs[group].publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = JointControlGUI()

    # 별도 스레드에서 ROS 데이터 수신 시작
    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    # 초기 데이터를 받을 때까지 대기 (최대 5초)
    import time
    start_time = time.time()
    while not node.got_initial_state and (time.time() - start_time) < 5.0:
        time.sleep(0.1)

    if node.got_initial_state:
        node.create_widgets()
        node.root.mainloop()
    else:
        print("에러: 로봇의 /joint_states 데이터를 받지 못했습니다. 드라이버가 켜져 있는지 확인하세요.")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()