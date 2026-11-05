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
    # SDL creates the main target before this subdirectory is processed,
    # so explicitly require C++23 on that existing target.
    target_compile_features(main PRIVATE cxx_std_23)
    # SDL's Android project owns libmain.so. Attach the title to that exact
    # target instead of creating a second shared library with the same name.
    target_sources(main PRIVATE
        ${RECVX_SOURCES}
        src/android_main.cpp
    )
    rexglue_setup_target(main GPU_PLUGINS xenos)
    # rex_app.cpp includes ImGui headers and ReXApp uses the SDK UI layer.
    # Linking rex::ui propagates imgui::imgui's include directory and includes
    # the UI object-library implementation in SDL's libmain.so.
    target_link_libraries(main PRIVATE rex::ui)
elseif(ANDROID)
    # Standalone Android mode is retained for non-SDL parent projects.
    add_library(recvx SHARED
        ${RECVX_SOURCES}
        src/android_main.cpp
    )
    set_target_properties(recvx PROPERTIES OUTPUT_NAME main)
    rexglue_setup_target(recvx GPU_PLUGINS xenos)
    target_link_libraries(recvx PRIVATE rex::ui)
elseif(WIN32)
    add_executable(recvx WIN32 ${RECVX_SOURCES})
    rexglue_setup_target(recvx GPU_PLUGINS xenos)
    target_link_libraries(recvx PRIVATE rex::ui)
else()
    add_executable(recvx ${RECVX_SOURCES})
    rexglue_setup_target(recvx GPU_PLUGINS xenos)
    target_link_libraries(recvx PRIVATE rex::ui)
endif()
