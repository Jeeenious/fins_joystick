/*******************************************************************************
 * py_bridge.hpp — C++ 可调用的手柄读取接口（按步调用，不阻塞）
 ******************************************************************************/
#pragma once

namespace py_bridge {

void init();
bool open_controller();
float get_lh();            // 左摇杆水平 (-1..1)
float get_lv();            // 左摇杆垂直 (-1..1)
float get_rh();            // 右摇杆水平 (-1..1)
float get_rv();            // 右摇杆垂直 (-1..1)
int   get_hat_x();         // 十字键 X (-1/0/1)
int   get_hat_y();         // 十字键 Y (-1/0/1)
bool  get_button(int idx); // 按钮 idx 是否按下
bool  pump_events();       // true 表示继续，false 表示 QUIT
void  close_controller();

}  // namespace py_bridge
