cmake_minimum_required(VERSION 3.0)
project(ds-server)

set(ds-server VERSION MAJOR 0)
set(ds-server VERSION MINOR 0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Werror -Wextra -pedantic -pedantic-errors")

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../cmake/modules ${CMAKE_MODULE_PATH})

include_directories("${PROJECT_SOURCE_DIR}/include")

set(DS_SERVER_SOURCE_FILES
	./src/main.cpp
)
add_executable(ds-server ${DS_SERVER_SOURCE_FILES})
