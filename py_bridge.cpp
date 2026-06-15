/*******************************************************************************
 * py_bridge.cpp — pybind11::embed 实现
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

  dlopen(PYTHON_LIBRARY_PATH, RTLD_NOW | RTLD_GLOBAL);
  if (!Py_IsInitialized())
    py::initialize_interpreter();

  py::module_ sys = py::module_::import("sys");
  sys.attr("path").attr("insert")(0, PY_PROJECT_DIR);

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
  static bool pg_inited = false;
  if (!pg_inited) {
    py::module_ os = py::module_::import("os");
    os.attr("environ")["SDL_VIDEODRIVER"] = "dummy";
    py::module_::import("pygame").attr("init")();
    pg_inited = true;
  }
  py::module_ m = py::module_::import("joystick_py.controller");
  g_ctrl = m.attr("RemoteController")();
  return g_ctrl.attr("open")().cast<bool>();
}

float py_bridge::get_lh() { return g_ctrl.attr("get_axes")().attr("__getitem__")(0).cast<float>(); }
float py_bridge::get_lv() { return g_ctrl.attr("get_axes")().attr("__getitem__")(1).cast<float>(); }
float py_bridge::get_rh() { return g_ctrl.attr("get_axes")().attr("__getitem__")(2).cast<float>(); }
float py_bridge::get_rv() { return g_ctrl.attr("get_axes")().attr("__getitem__")(3).cast<float>(); }
int   py_bridge::get_hat_x()  { return g_ctrl.attr("get_hat")().attr("__getitem__")(0).cast<int>(); }
int   py_bridge::get_hat_y()  { return g_ctrl.attr("get_hat")().attr("__getitem__")(1).cast<int>(); }
bool  py_bridge::get_button(int idx) { return g_ctrl.attr("is_button_down")(idx).cast<bool>(); }

bool py_bridge::pump_events() {
  py::module_ pygame = py::module_::import("pygame");
  py::list events = pygame.attr("event").attr("get")();
  for (auto e : events)
    if (e.attr("type").cast<int>() == pygame.attr("QUIT").cast<int>()) return false;
  return true;
}

void py_bridge::close_controller() {
  py::module_::import("pygame").attr("quit")();
}
