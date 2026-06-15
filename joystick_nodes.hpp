/*******************************************************************************
 * joystick_nodes.hpp — Joystick 手柄数据源 FINS 节点
 ******************************************************************************/

#pragma once

#include <atomic>
#include <chrono>
#include <thread>

#include <fins/node.hpp>
#include "py_bridge.hpp"

class JoystickSource : public fins::Node {
public:
  void define() override {
    set_name("JoystickSource");
    set_description("读取游戏手柄，输出摇杆/十字键/按钮");
    set_category("Joystick");
    register_output<float>("lh");
    register_output<float>("lv");
    register_output<float>("rh");
    register_output<float>("rv");
    register_output<int>("hat_x");
    register_output<int>("hat_y");
    register_output<bool>("btn_4");
    register_output<bool>("btn_5");
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
        logger->warn("手柄初始化失败");
        running_ = false;
        return;
      }
      logger->info("JoystickSource 开始输出 @10Hz.");

      int tick = 0;
      while (running_) {
        if (!py_bridge::pump_events()) { running_ = false; break; }
        send("lh", py_bridge::get_lh()); send("lv", py_bridge::get_lv());
        send("rh", py_bridge::get_rh()); send("rv", py_bridge::get_rv());
        send("hat_x", py_bridge::get_hat_x()); send("hat_y", py_bridge::get_hat_y());
        send("btn_4", py_bridge::get_button(4));
        send("btn_5", py_bridge::get_button(5));
        if (++tick % 10 == 0)
          logger->info("Joy: axes={:.2f},{:.2f},{:.2f},{:.2f}",
            py_bridge::get_lh(), py_bridge::get_lv(), py_bridge::get_rh(), py_bridge::get_rv());
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
      }
    });
  }

  void pause() override {
    running_ = false;
    if (worker_.joinable()) worker_.detach();
    logger->info("JoystickSource 已暂停.");
  }

private:
  std::thread worker_;
  std::atomic<bool> running_{false};
};
EXPORT_NODE(JoystickSource)
