/*******************************************************************************
 * py_bridge.hpp — C++ 可调用的手柄读取接口（按步调用，不阻塞）
 ******************************************************************************/
#pragma once

#include <string>

namespace py_bridge {

void init();
bool open_controller();
std::string get_axes();       // "lh,lv,rh,rv"
std::string get_hat();         // "hx,hy"
std::string get_buttons();     // "b1,b2,..."
bool pump_events();            // true 表示继续，false 表示 QUIT
void close_controller();

}  // namespace py_bridge
