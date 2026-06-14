/*******************************************************************************
 * joystick_nodes.hpp — Joystick 手柄数据源 FINS 节点
 *
 * 输出端口:
 *   lh / lv / rh / rv    → float   摇杆四轴 (-1..1)
 *   hat_x / hat_y        → int     十字键 (-1/0/1)
 *   btn_0 .. btn_15     → bool    按钮按下状态
 ******************************************************************************/

#pragma once

#include <atomic>
#include <chrono>
#include <string>
#include <thread>

#include <fins/node.hpp>
#include "py_bridge.hpp"

class JoystickSource : public fins::Node {
public:
  JoystickSource() = default;

  void define() override {
    set_name("JoystickSource");
    set_description("读取游戏手柄，输出原始摇杆/十字键/按钮数据");
    set_category("Joystick");
    register_output<float>("lh");
    register_output<float>("lv");
    register_output<float>("rh");
    register_output<float>("rv");
    register_output<int>("hat_x");
    register_output<int>("hat_y");
    for (int i = 0; i < 16; ++i)
      register_output<bool>("btn_" + std::to_string(i));
  }

  void initialize() override {
    logger->info("JoystickSource 初始化.");
    running_ = false;
  }

  void run() override {
    if (running_) return;
    running_ = true;

    worker_ = std::thread([this]() {
      if (!py_bridge::open_controller()) {
        logger->warn("手柄初始化失败，请检查手柄连接。");
        running_ = false;
        return;
      }
      logger->info("JoystickSource 开始输出手柄数据 @30Hz.");

      while (running_) {
        if (!py_bridge::pump_events()) {
          running_ = false;
          break;
        }

        send("lh", py_bridge::get_lh());
        send("lv", py_bridge::get_lv());
        send("rh", py_bridge::get_rh());
        send("rv", py_bridge::get_rv());
        send("hat_x", py_bridge::get_hat_x());
        send("hat_y", py_bridge::get_hat_y());
        for (int i = 0; i < 16; ++i)
          send("btn_" + std::to_string(i), py_bridge::get_button(i));

        std::this_thread::sleep_for(std::chrono::milliseconds(33));
      }
    });
  }

  void pause() override {
    running_ = false;
    if (worker_.joinable()) worker_.join();
    py_bridge::close_controller();
    logger->info("JoystickSource 已暂停.");
  }

  void reset() override { logger->info("JoystickSource 重置."); }

private:
  std::thread worker_;
  std::atomic<bool> running_{false};
};

EXPORT_NODE(JoystickSource)
