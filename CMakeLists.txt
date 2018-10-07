cmake_minimum_required(VERSION 3.0)
project(your-print-is-ready)

set(your-print-is-ready VERSION MAJOR 0)
set(your-print-is-ready VERSION MINOR 0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17 -Wall -Werror -Wextra -pedantic -pedantic-errors")

set (CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules ${CMAKE_MODULE_PATH})

add_definitions (-DRASPBERRYPI)
find_package(WiringPi REQUIRED)
set (FLAGS "-DRASPBERRYPI")
include_directories (${WIRINGPI_INCLUDE_DIR})

include_directories("${PROJECT_SOURCE_DIR}/include")

set (POLLER_PI_SOURCE_FILES
	./src/poller-pi/main.cpp
)
add_executable(poller-pi ${POLLER_PI_SOURCE_FILES})
target_link_libraries(poller-pi ${WIRINGPI_LIBRARIES})

set (DS_SERVER_SOURCE_FILES
	./src/ds-server/main.cpp
)
add_executable(ds-server ${DS_SERVER_SOURCE_FILES})
