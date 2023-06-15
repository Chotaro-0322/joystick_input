import threading
import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32

import time
import pygame

class JoystickPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.speed_publisher = self.create_publisher(Float32, 'robocar_speed', 10)
        self.steering_publisher = self.create_publisher(Float32, 'robocar_steering', 10)
        # pygame setting
        pygame.init()
        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()
        self.joystick_state = {"□" : 0, "x" : 0, "o" : 0, "△" : 0,
                                "L1" : 0,"R1" : 0,
                                "arrow" : [0.0, 0.0],
                                "left_stick" : [0.0, 0.0]
                                }

    def button_thread(self):
        while True:
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.joystick_state["x"] = 1
                        print("xボタンが押されました")

                    elif event.button == 1:
                        self.joystick_state["o"] = 1
                        print("oボタンが押されました")

                    elif event.button == 2:
                        self.joystick_state["□"] = 1
                        print("四角ボタンが押されました")

                    elif event.button == 3:
                        self.joystick_state["△"] = 1
                        print("三角ボタンが押されました")

                    elif event.button == 4:
                        self.joystick_state["L1"] = 1
                        print("L1が押されました")

                    elif event.button == 5:
                        self.joystick_state["R1"] = 1
                        print("R1が押されました")

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 0:
                        self.joystick_state["x"] = 0
                        print("xボタンが離されました")

                    elif event.button == 1:
                        self.joystick_state["o"] = 0
                        print("oボタンが離されました")

                    elif event.button == 2:
                        self.joystick_state["□"] = 0
                        print("四角ボタンが離されました")

                    elif event.button == 3:
                        self.joystick_state["△"] = 0
                        print("三角ボタンが離されました")

                    elif event.button == 4:
                        self.joystick_state["L1"] = 0
                        print("L1が離されました")

                    elif event.button == 5:
                        self.joystick_state["R1"] = 0
                        print("R1が離されました")

                if event.type == pygame.JOYHATMOTION:
                    # print("十字キー座標")
                    # print("("+str((j.get_hat(0))[0])+","+str((j.get_hat(0))[1])+")")
                    self.joystick_state["arrow"] = [(self.joy.get_hat(0))[0], (self.joy.get_hat(0))[1]]

                elif event.type == pygame.JOYAXISMOTION:
                    if (abs((self.joy.get_axis(0))) >= 0.2) or (abs((self.joy.get_axis(1))) >= 0.2):
                        # print("左スティック座標")
                        # print("("+str(j.get_axis(0))+","+ str(j.get_axis(1))+")")
                        self.joystick_state["left_stick"] = [self.joy.get_axis(0), self.joy.get_axis(1)]
                    else:
                        self.joystick_state["left_stick"] = [0, 0]

            time.sleep(0.1)
            # print(self.joystick_state)

    def publish_thread(self):
        # ステアリング角とスピードの決定
        max_speed = 1000.0
        target_speed = 500.0
        speed_mmpsec = 500.0
        max_steering = 30.0 # 左右それぞれの最大操舵角
        while True:
            # oを押したらアクセル
            if self.joystick_state["o"] == 1: 
                speed_mmpsec += 50
            else: # oを話したら徐々に減速
                speed_mmpsec -= 50

            # xを押したらブレーキ
            if self.joystick_state["x"]:
                speed_mmpsec -= 200.0

            # 操舵角 [横, 縦]
            if self.joystick_state["left_stick"] != [0, 0]: 
                steering_deg = max_steering * self.joystick_state["left_stick"][0]
            else:
                steering_deg = 0.0

            # 目標速度の変更
            if self.joystick_state["arrow"] == [0, 1]: 
                target_speed += 10.0
                if target_speed > max_speed:
                    target_speed = max_speed
            elif self.joystick_state["arrow"] == [0, -1]:
                target_speed -= 10.0
                if target_speed < 0:
                    target_speed = 0.0
            
            # スピードが上限を超えないように制限
            if speed_mmpsec < 0:
                speed_mmpsec = 0.0
            elif speed_mmpsec > target_speed:
                speed_mmpsec = target_speed

            print("(speed, steering) : ({}, {})".format(speed_mmpsec, steering_deg))

            # データのpublish
            robocar_speed_msg = Float32()
            robocar_steering_msg = Float32()

            robocar_speed_msg.data= speed_mmpsec
            robocar_steering_msg.data = steering_deg

            self.speed_publisher.publish(robocar_speed_msg)
            self.steering_publisher.publish(robocar_steering_msg)
            
            time.sleep(0.1)
        # except:
        #     pass

def main(args=None):
    rclpy.init(args=args)
    joystick_publisher = JoystickPublisher()
    button_thread = threading.Thread(target=joystick_publisher.button_thread)
    button_thread.start()
    publish_thread = threading.Thread(target=joystick_publisher.publish_thread)
    publish_thread.start()
    rclpy.spin(joystick_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    joystick_publisher.destroy_node()

    rclpy.shutdown()

if __name__ == '__main__':

    main()