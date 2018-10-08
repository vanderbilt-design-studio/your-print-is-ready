cmake_minimum_required(VERSION 3.0)
project(poller-pi)

set(poller-pi VERSION MAJOR 0)
set(poller-pi VERSION MINOR 0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Werror -Wextra -pedantic -pedantic-errors")

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../cmake/modules ${CMAKE_MODULE_PATH})

# Create a variable that holds the path to our libwiringPi.so file
set (WPI_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../libs/wiringPi/wiringPi)
# Add the local ‘include’ directory and the wiringPi directory to grab headers
include_directories (include ${WPI_PATH})
# Actually find the wiringPi library object
find_library(WPI_LIB wiringPi HINTS ${WPI_PATH} NO_CMAKE_FIND_ROOT_PATH)
# Alert the user if we do not find it
if(NOT WPI_LIB)
 message(FATAL_ERROR “wiringPi library not found”)
endif()


include_directories("${PROJECT_SOURCE_DIR}/include")

set(POLLER_PI_SOURCE_FILES
	./src/main.cpp
)
add_executable(poller-pi ${POLLER_PI_SOURCE_FILES})
target_link_libraries(poller-pi ${WPI_LIB})
