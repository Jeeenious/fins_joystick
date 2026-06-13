# fins-joystick

FINS 手柄数据源插件，读取游戏手柄输入并输出原始摇杆/十字键/按钮数据到管道。

## 架构

```
joystick_py/  (Python — 仅物理层读取)
  controller.py   → RemoteController — pygame 手柄驱动
  config.py       → 从 config/config.yaml 加载参数

py_bridge.cpp  (pybind11 桥接)
  open_controller()  → 创建 RemoteController，打开手柄
  pump_events()      → 泵取 pygame 事件队列
  get_axes()         → 读取四轴: lh,lv,rh,rv
  get_hat()          → 读取十字键: hx,hy
  get_buttons()      → 读取按下按钮编号列表
  close_controller() → 关闭手柄

joystick_nodes.hpp  (C++ FINS 节点)
  JoystickSource → C++ 控制循环，定时读取并输出到管道
```

## 定时取数实现

整个控制循环在 **C++ 层**，不走 Python 循环：

```
FINS 框架调用 run()
  └→ 启动 std::thread worker
       └→ py_bridge::open_controller()    // 打开手柄
       └→ while (running_) {              // C++ 循环
            py_bridge::pump_events()       // 泵 pygame 事件
            axes   = py_bridge::get_axes()
            hat    = py_bridge::get_hat()
            btns   = py_bridge::get_buttons()
            send("axes", axes)             // → FINS 管道
            send("hat", hat)
            send("buttons", btns)
            sleep(33ms)                    // ~30Hz
          }
```

每秒约 30 次从手柄读取数据并通过 FINS 管道广播。`sleep_for(33ms)` 控制帧率，可通过 `config/config.yaml` 中的 `control.fps` 调整。

## 输出端口

| 端口        | 格式                         | 示例                     |
| --------- | -------------------------- | ---------------------- |
| `axes`    | `左水平,左垂直,右水平,右垂直`(float×4) | `0.52,-0.31,0.10,0.85` |
| `hat`     | `十字键X,十字键Y`(int×2, -1/0/1) | `0,1`                  |
| `buttons` | 按下按钮编号列表(int,...)          | `4,7`                  |

## 管线组合

```
JoystickSource → axes/hat/buttons → fins_joystick_solver → motion/servo/gripper → fins_serial → TCP
```

## 编译

```bash
fins build fins_joystick
```

## 依赖

- pybind11
- pygame（`pip install pygame`）
