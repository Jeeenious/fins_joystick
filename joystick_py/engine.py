# -*- coding: utf-8 -*-
"""
JoystickEngine — 可被 C++ pybind11 调用的控制循环。
替代原 main.py，去掉 visualizer，提供 start/stop 接口。
"""
import threading
import time
import pygame

from .config import (
    PROPELLER_ADDR, CMD_TOGGLE_FLOAT, CMD_TOGGLE_YAW_LOOP,
    GRIPPER_CLOSE_BUTTON, GRIPPER_OPEN_BUTTON,
    GRIPPER_REPEAT_INTERVAL, SERVO_REPEAT_INTERVAL,
    SERVO_X_INDEX, SERVO_Y_INDEX, FPS,
)
from .controller import RemoteController
from .solver import solve_motion, solve_servo, solve_gripper
from .tcp_sender import (
    connect, send_pkt, send_servo_pwm, send_gripper_speed,
    send_combined_motion,
)
from .tcp_receiver import recv_worker
from . import tcp_receiver

_engine_instance = None


class JoystickEngine:
    """手柄控制引擎，封装完整的 30FPS 控制循环。"""

    def __init__(self):
        self._running = False
        self._ctrl = None
        self._rx_thread = None

    def init(self) -> bool:
        """TCP 连接 + 手柄初始化。成功返回 True。"""
        connect()
        pygame.init()
        self._ctrl = RemoteController()
        if not self._ctrl.open():
            print("[JoystickEngine] No joystick found.")
            return False
        print(f"[JoystickEngine] Using joystick: {self._ctrl.get_name()}")
        return True

    def run(self):
        """30FPS 控制循环（阻塞），直到调用 stop()。"""
        self._running = True
        self._rx_thread = threading.Thread(target=recv_worker, daemon=True)
        self._rx_thread.start()

        is_hovering = False
        is_yaw_looping = False
        bbbb = 1500
        cccc = 1500
        hat_state = (0, 0)
        last_combined = (0, 0, 0, 0)
        last_gripper_dir = 0
        last_gripper_tick = 0.0
        last_servo_tick = 0.0

        clock = pygame.time.Clock()

        while self._running:
            now = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.JOYHATMOTION:
                    hat_state = self._ctrl.get_hat()
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 7:
                        is_hovering = not is_hovering
                        send_pkt(PROPELLER_ADDR, CMD_TOGGLE_FLOAT,
                                 bytes([1 if is_hovering else 0]))
                    elif event.button == 0:
                        is_yaw_looping = not is_yaw_looping
                        send_pkt(PROPELLER_ADDR, CMD_TOGGLE_YAW_LOOP,
                                 bytes([1 if is_yaw_looping else 0]))

            axes = self._ctrl.get_axes()
            motion = solve_motion(axes)

            combined = (motion["x_pct"], motion["y_pct"],
                        motion["yaw_rate_cmd"], motion["depth_force_cmd"])
            if is_hovering and combined != last_combined:
                send_combined_motion(*combined)
                last_combined = combined

            gdir = solve_gripper(self._ctrl, GRIPPER_CLOSE_BUTTON, GRIPPER_OPEN_BUTTON)
            if gdir != last_gripper_dir or (
                gdir != 0 and now - last_gripper_tick >= GRIPPER_REPEAT_INTERVAL
            ):
                send_gripper_speed(gdir)
                last_gripper_dir = gdir
                last_gripper_tick = now

            if hat_state != (0, 0) and (now - last_servo_tick >= SERVO_REPEAT_INTERVAL):
                bbbb, cccc, changed = solve_servo(hat_state, bbbb, cccc)
                if changed:
                    send_servo_pwm(SERVO_X_INDEX, bbbb)
                    send_servo_pwm(SERVO_Y_INDEX, cccc)
                last_servo_tick = now

            clock.tick(FPS)

    def stop(self):
        """停止控制循环并清理资源。"""
        self._running = False
        if self._rx_thread and self._rx_thread.is_alive():
            tcp_receiver.rx_stop = True
            self._rx_thread.join(timeout=2)
        try:
            from .tcp_sender import sock
            if sock:
                sock.close()
        except Exception:
            pass


def get_engine():
    """获取全局引擎实例（C++ 通过 pybind11 调用）。"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = JoystickEngine()
    return _engine_instance
