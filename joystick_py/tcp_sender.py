# -*- coding: utf-8 -*-
"""
TCP 下发：连接管理 + 二进制协议组帧 + 命令发送。
"""
import socket
import time
import struct
from collections import deque

from .config import (
    PI_IP, PI_PORT,
    FRAME_HEADER, PROPELLER_ADDR, SERVO_ADDR, GRIPPER_ADDR,
    CMD_SET_SERVO_PWM, CMD_GRIPPER_SPEED, CMD_SET_COMBINED_MOTION,
)

sock = None
send_log = deque(maxlen=12)


# ── 连接 ──

def connect():
    """连接树莓派，断线死循环重试。"""
    global sock
    while True:
        try:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((PI_IP, PI_PORT))
            sock = s
            print(f"[NET] Connected to {PI_IP}:{PI_PORT}")
            log(f"# Connected {PI_IP}:{PI_PORT}")
            return
        except Exception as e:
            print(f"[NET] Connect failed: {e}, retrying...")
            time.sleep(3)


# ── 协议编码 ──

def crc16_modbus(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
            crc &= 0xFFFF
    return crc


def build_frame(addr, cmd, payload=b""):
    payload = bytes(payload)
    if len(payload) > 255:
        raise ValueError("payload length must be <= 255")
    body = bytes([addr & 0xFF, cmd & 0xFF, len(payload) & 0xFF]) + payload
    crc = crc16_modbus(body)
    return FRAME_HEADER + body + struct.pack("<H", crc)


def i16le(val):
    return struct.pack("<h", int(val))


def i8(val):
    return struct.pack("b", int(max(-128, min(127, int(val)))))


# ── 字符串发送 ──

def send_tcp(msg):
    data = (msg + "\n").encode()
    try:
        sock.sendall(data)
        log(msg)
    except Exception as e:
        print(f"[NET] Send failed: {e}")
        connect()


# ── 二进制协议发送 ──

def send_pkt(addr, cmd, payload=b""):
    frame = build_frame(addr, cmd, payload)
    try:
        sock.sendall(frame)
        log(f"TX data={frame.hex(' ')}")
    except Exception as e:
        print(f"[NET] Send failed: {e}")
        connect()


def send_servo_pwm(index, pwm):
    send_pkt(SERVO_ADDR, CMD_SET_SERVO_PWM, bytes([index & 0xFF]) + i16le(pwm))


def send_gripper_speed(direction):
    if direction > 0:
        direction = 1
    elif direction < 0:
        direction = -1
    else:
        direction = 0
    send_pkt(GRIPPER_ADDR, CMD_GRIPPER_SPEED, i8(direction))


def send_combined_motion(x_pct, y_pct, yaw_rate, depth_force):
    payload = i8(x_pct) + i8(y_pct) + i16le(yaw_rate) + i16le(depth_force)
    send_pkt(PROPELLER_ADDR, CMD_SET_COMBINED_MOTION, payload)


# ── 日志 ──

def log(msg):
    ts = time.strftime("%H:%M:%S")
    send_log.appendleft(f"{ts}  {msg}")
