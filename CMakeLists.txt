# Resident Evil Code: Veronica X HD - ReXGlue recompiled project

cmake_minimum_required(VERSION 3.25)
project(recvx LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(generated/rexglue.cmake)

set(RECVX_SOURCES
    src/main.cpp
)

if(ANDROID AND TARGET main)
    # SDL's Android project owns libmain.so. Attach the title to that exact
    # target instead of creating a second shared library with the same name.
    target_sources(main PRIVATE
        ${RECVX_SOURCES}
        src/android_main.cpp
    )
    rexglue_setup_target(main GPU_PLUGINS xenos)
elseif(ANDROID)
    # Standalone Android mode is retained for non-SDL parent projects.
    add_library(recvx SHARED
        ${RECVX_SOURCES}
        src/android_main.cpp
    )
    set_target_properties(recvx PROPERTIES OUTPUT_NAME main)
    if(NOT ANDROID)
    rexglue_setup_target(recvx GPU_PLUGINS xenos)
endif()
elseif(WIN32)
    add_executable(recvx WIN32 ${RECVX_SOURCES})
else()
    add_executable(recvx ${RECVX_SOURCES})
endif()

rexglue_setup_target(recvx GPU_PLUGINS xenos)
