# -*- coding: utf-8 -*-
"""
遥控器类：封装 pygame 手柄的读取操作。
"""
import pygame


class RemoteController:
    """读取游戏手柄的摇杆、按键、十字键。"""

    def __init__(self):
        self.js = None

    def open(self):
        """查找并初始化第一个手柄。返回 True 表示成功。"""
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            return False
        self.js = pygame.joystick.Joystick(0)
        self.js.init()
        return True

    def get_name(self):
        return self.js.get_name() if self.js else "N/A"

    def get_axes(self):
        """返回 (leftH, leftV, rightH, rightV)，异常时全 0。"""
        try:
            return (
                self.js.get_axis(0),
                self.js.get_axis(1),
                self.js.get_axis(2),
                self.js.get_axis(3),
            )
        except Exception:
            return (0.0, 0.0, 0.0, 0.0)

    def get_hat(self):
        return self.js.get_hat(0) if self.js else (0, 0)

    def get_pressed_buttons(self):
        """返回所有当前按下的按钮编号列表。"""
        if not self.js:
            return []
        return [i for i in range(self.js.get_numbuttons()) if self.js.get_button(i)]

    def is_button_down(self, index):
        """安全读取单个按钮，越界返回 False。"""
        return bool(self.js) and 0 <= index < self.js.get_numbuttons() and self.js.get_button(index)
