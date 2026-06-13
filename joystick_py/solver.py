# -*- coding: utf-8 -*-
"""
速度解算：将摇杆原始值映射为推力百分比 (-99..99)。
"""
from .config import (
    DIRECTION_THRESHOLD, DEPTH_THRESHOLD, ROTATE_THRESHOLD,
    MAX_SPEED, PWM_MIN, PWM_MAX, SERVO_STEP,
)


def calculate_speed(axis_value, threshold):
    """摇杆值 → 百分比，带死区。"""
    speed = 0
    if not -threshold < axis_value < threshold:
        if axis_value > 0:
            speed = int((axis_value - threshold) * MAX_SPEED / (1 - threshold))
        else:
            speed = -int((-axis_value - threshold) * MAX_SPEED / (1 - threshold))
    return speed


def solve_motion(axes):
    """
    解算四个摇杆轴 → 控制命令。
    返回 dict: {x_pct, y_pct, yaw_rate_cmd, depth_force_cmd}
    """
    leftH, leftV, rightH, rightV = axes
    return {
        "x_pct": calculate_speed(leftH, DIRECTION_THRESHOLD),
        "y_pct": -calculate_speed(leftV, DIRECTION_THRESHOLD),
        "yaw_rate_cmd": calculate_speed(rightH, ROTATE_THRESHOLD)
        if not (-ROTATE_THRESHOLD < rightH < ROTATE_THRESHOLD) else 0,
        "depth_force_cmd": calculate_speed(rightV, DEPTH_THRESHOLD)
        if not (-DEPTH_THRESHOLD < rightV < DEPTH_THRESHOLD) else 0,
    }


def solve_servo(hat, bbbb, cccc):
    """
    十字键 → 舵机 PWM 增量。
    返回 (new_bbbb, new_cccc, changed)
    """
    hx, hy = hat
    changed = False
    if hy == 1:
        bbbb = min(bbbb + SERVO_STEP, PWM_MAX)
        changed = True
    elif hy == -1:
        bbbb = max(bbbb - SERVO_STEP, PWM_MIN)
        changed = True
    if hx == 1:
        cccc = min(cccc + SERVO_STEP, PWM_MAX)
        changed = True
    elif hx == -1:
        cccc = max(cccc - SERVO_STEP, PWM_MIN)
        changed = True
    return bbbb, cccc, changed


def solve_gripper(controller, close_btn, open_btn):
    """读取夹爪按钮 → 方向: 1闭合 / -1张开 / 0停止"""
    close = controller.is_button_down(close_btn)
    open_ = controller.is_button_down(open_btn)
    if close and not open_:
        return 1
    if open_ and not close:
        return -1
    return 0
