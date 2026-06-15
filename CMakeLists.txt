cmake_minimum_required(VERSION 3.16)

project(fins_joystick)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

execute_process(
  COMMAND ${Python3_EXECUTABLE} -c
    "import sysconfig; print(sysconfig.get_config_var('LIBDIR') + '/' + sysconfig.get_config_var('LDLIBRARY'))"
  OUTPUT_VARIABLE PYTHON_LIBRARY_PATH
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

fins_add_node(${PROJECT_NAME} nodes.cpp py_bridge.cpp)

target_compile_definitions(${PROJECT_NAME} PRIVATE
  PY_PROJECT_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
  PYTHON_LIBRARY_PATH="${PYTHON_LIBRARY_PATH}"
)

target_include_directories(${PROJECT_NAME} PRIVATE
  ${Python3_INCLUDE_DIRS}
  ${pybind11_INCLUDE_DIRS}
)

target_link_options(${PROJECT_NAME} PRIVATE -rdynamic)

target_link_libraries(${PROJECT_NAME} PRIVATE
  pybind11::embed
  ${Python3_LIBRARIES}
)
