# -*- coding: utf-8 -*-
"""
TCP 接收：后台线程持续读取下位机数据，写入日志文件。
注意：线程由 main.py 创建，本文件只提供工作函数。
"""
import time
from collections import deque

from . import tcp_sender

recv_log = deque(maxlen=20)
latest_gripper_pwm = None
rx_stop = False
_log_file = "recv_log.txt"


def recv_worker():
    """后台循环：读 TCP → 按行解析 → 写日志。由 main.py 启动为线程。"""
    global latest_gripper_pwm, rx_stop
    buf = b""
    while not rx_stop:
        try:
            data = tcp_sender.sock.recv(1024)
            if not data:
                _log("# 连接丢失，正在重连...")
                tcp_sender.connect()
                continue
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode(errors="ignore").strip("\r")
                if text:
                    _log(text)
                    # 解析回传数据中的夹爪 PWM
                    try:
                        parts = [p.strip() for p in text.split(",")]
                        if len(parts) >= 4:
                            latest_gripper_pwm = int(float(parts[-1]))
                    except ValueError:
                        pass
        except Exception as e:
            _log(f"# 接收错误: {e}")
            time.sleep(1)


def _log(msg):
    """记录到 recv_log 队列和文件。"""
    ts = time.strftime("%H:%M:%S")
    line = f"{ts}  {msg}"
    recv_log.appendleft(line)
    try:
        with open(_log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[FILE] 写入日志失败: {e}")
