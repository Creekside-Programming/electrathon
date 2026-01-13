cmake_minimum_required(VERSION 3.22)

include(thirdparty/pico-sdk/pico_sdk_init.cmake) # must happen before project()

# --- project configuration ---
project(electrathon-car VERSION 1.0 LANGUAGES C CXX) # we need C for the pico sdk

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

pico_sdk_init()

# --- libraries ---
# radiolib
set(RADIOLIB_BUILD_ARDUINO OFF CACHE BOOL "" FORCE)
set(RADIOLIB_BUILD_LINUX OFF CACHE BOOL "" FORCE)
set(RADIOLIB_BUILD_RPI_PICO ON CACHE BOOL "" FORCE)
add_subdirectory(thirdparty/RadioLib)
target_sources(RadioLib PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/RadioLib/src/hal/RPiPico/PicoHal.cpp
)
target_link_libraries(RadioLib PUBLIC
    pico_stdlib
    hardware_spi
    hardware_pwm
    pico_multicore
)
target_compile_definitions(RadioLib PUBLIC
    RADIOLIB_BUILD_RPI_PICO=1
)

add_subdirectory(src)

add_executable(electrathon-car ${SOURCE_FILES})

target_link_libraries(electrathon-car PRIVATE 
    RadioLib 
    pico_stdlib
    hardware_spi
    hardware_pwm
)

pico_add_extra_outputs(electrathon-car)