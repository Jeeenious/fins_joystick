cmake_minimum_required(VERSION 3.16)

project(fins_joystick)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

fins_add_node(${PROJECT_NAME} nodes.cpp py_bridge.cpp)

target_compile_definitions(${PROJECT_NAME} PRIVATE
  PY_PROJECT_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
)

target_include_directories(${PROJECT_NAME} PRIVATE
  ${Python3_INCLUDE_DIRS}
  ${pybind11_INCLUDE_DIRS}
)

target_link_libraries(${PROJECT_NAME} PRIVATE
  pybind11::embed
  Python3::Python
)
