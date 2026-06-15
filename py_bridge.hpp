/*******************************************************************************
 * py_bridge.hpp — C++ 可调用的手柄读取接口
 ******************************************************************************/
#pragma once

#include <vector>

namespace py_bridge {

void init();
bool open_controller();
float get_lh(); float get_lv(); float get_rh(); float get_rv();
int   get_hat_x(); int get_hat_y();
bool  get_button(int idx);
bool  pump_events();
void  close_controller();

}  // namespace py_bridge
