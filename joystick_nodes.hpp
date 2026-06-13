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
  JoystickSource() = default;

  void define() override {
    set_name("JoystickSource");
    set_description("读取游戏手柄，输出原始摇杆/十字键/按钮数据");
    set_category("Joystick");
    register_output<std::string>("axes");
    register_output<std::string>("hat");
    register_output<std::string>("buttons");
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

        auto axes = py_bridge::get_axes();
        auto hat = py_bridge::get_hat();
        auto btns = py_bridge::get_buttons();

        if (!axes.empty()) send("axes", axes);
        if (!hat.empty()) send("hat", hat);
        if (!btns.empty()) send("buttons", btns);

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
