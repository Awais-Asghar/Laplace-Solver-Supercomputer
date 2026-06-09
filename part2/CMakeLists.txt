cmake_minimum_required(VERSION 2.8)
project(LaplaceSolverHPC CXX)

# ---- Compiler flags (no C++11/17, plain C++03) ----
set(CMAKE_CXX_FLAGS "-O2 -Wall")

# ---- Find MPI ----
find_package(MPI REQUIRED)
message(STATUS "MPI found: ${MPI_CXX_COMPILER}")
include_directories(${MPI_CXX_INCLUDE_PATH})

# ---- Find OpenMP ----
find_package(OpenMP REQUIRED)
message(STATUS "OpenMP found")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")

# ---- Serial solver ----
add_executable(laplace_serial src/laplace_serial.cpp)
target_link_libraries(laplace_serial rt)

# ---- MPI solver ----
add_executable(laplace_mpi src/laplace_mpi.cpp)
target_link_libraries(laplace_mpi ${MPI_CXX_LIBRARIES} rt)

# ---- OpenMP solver ----
add_executable(laplace_omp src/laplace_omp.cpp)
target_link_libraries(laplace_omp rt)

message(STATUS "")
message(STATUS "Build complete. Usage:")
message(STATUS "  Serial  : ./laplace_serial [N] [epochs] [tol]")
message(STATUS "  MPI     : mpirun -n 4 ./laplace_mpi [N] [epochs] [tol]")
message(STATUS "  OpenMP  : ./laplace_omp [N] [epochs] [tol] [threads]")
message(STATUS "  Verify  : python3 ../src/verify_correctness.py [N]")
message(STATUS "  Bench   : python3 ../src/benchmark.py")
message(STATUS "")