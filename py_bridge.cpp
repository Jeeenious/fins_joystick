/*******************************************************************************
 * py_bridge.cpp — pybind11::embed 实现，按步调 joystick_py.controller
 ******************************************************************************/

#include "py_bridge.hpp"
#include <pybind11/embed.h>
#include <pybind11/stl.h>
#include <dlfcn.h>

namespace py = pybind11;

static py::object g_ctrl;

void py_bridge::init() {
  static bool inited = false;
  if (inited) return;
  inited = true;

  // CMake 编译时自动探测 libpython 路径，注入全局符号表使 C 扩展可用
  dlopen(PYTHON_LIBRARY_PATH, RTLD_NOW | RTLD_GLOBAL);

  if (!Py_IsInitialized())
    py::initialize_interpreter();

  py::module_ sys = py::module_::import("sys");
  py::list path = sys.attr("path");
  path.attr("insert")(0, PY_PROJECT_DIR);

  try {
    py::module_::import("joystick_py.controller");
    py::print("[py_bridge] joystick_py 导入成功");
  } catch (py::error_already_set &e) {
    py::print("[py_bridge] Python 导入失败:", e.what());
    throw;
  }
}

bool py_bridge::open_controller() {
  init();
  py::module_ m = py::module_::import("joystick_py.controller");
  g_ctrl = m.attr("RemoteController")();
  return g_ctrl.attr("open")().cast<bool>();
}

float py_bridge::get_lh() { init(); return g_ctrl.attr("get_axes")().attr("__getitem__")(0).cast<float>(); }
float py_bridge::get_lv() { init(); return g_ctrl.attr("get_axes")().attr("__getitem__")(1).cast<float>(); }
float py_bridge::get_rh() { init(); return g_ctrl.attr("get_axes")().attr("__getitem__")(2).cast<float>(); }
float py_bridge::get_rv() { init(); return g_ctrl.attr("get_axes")().attr("__getitem__")(3).cast<float>(); }

int py_bridge::get_hat_x() {
  init();
  return g_ctrl.attr("get_hat")().attr("__getitem__")(0).cast<int>();
}

int py_bridge::get_hat_y() {
  init();
  return g_ctrl.attr("get_hat")().attr("__getitem__")(1).cast<int>();
}

bool py_bridge::get_button(int idx) {
  init();
  return g_ctrl.attr("is_button_down")(idx).cast<bool>();
}

bool py_bridge::pump_events() {
  init();
  py::module_ pygame = py::module_::import("pygame");
  py::list events = pygame.attr("event").attr("get")();
  for (auto e : events) {
    if (e.attr("type").cast<int>() == pygame.attr("QUIT").cast<int>())
      return false;
  }
  return true;
}

void py_bridge::close_controller() {
  init();
  py::module_::import("pygame").attr("quit")();
}
