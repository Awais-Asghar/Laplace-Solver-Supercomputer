#!/bin/bash
# ============================================================
# run_all.sh
# Master script: compile everything, verify correctness,
# run benchmarks, generate plots.
# Run this from inside the build/ directory.
# ============================================================

set -e  # exit on error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/part2/build"
SRC_DIR="$SCRIPT_DIR/part2/src"
RESULTS_DIR="$SCRIPT_DIR/part2/results"

mkdir -p "$BUILD_DIR" "$RESULTS_DIR"

echo "============================================"
echo "  Step 1: Build with CMake"
echo "============================================"
cd "$BUILD_DIR"
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
echo "Build successful."

echo ""
echo "============================================"
echo "  Step 2: Verify Correctness (N=32)"
echo "============================================"
cd "$RESULTS_DIR"
cp "$BUILD_DIR/laplace_serial" .
cp "$BUILD_DIR/laplace_mpi" .
cp "$BUILD_DIR/laplace_omp" .
cp "$SRC_DIR/verify_correctness.py" .
cp "$SRC_DIR/benchmark.py" .

./laplace_serial 32 10000 1e-4
mpirun -n 4 ./laplace_mpi 32 10000 1e-4
./laplace_omp 32 10000 1e-4 4
python3 verify_correctness.py 32

echo ""
echo "============================================"
echo "  Step 3: Run Benchmarks"
echo "============================================"
# Initialize timing files
echo "N,Procs,Epochs,Time_s" > mpi_timing.csv
echo "N,Threads,Epochs,Time_s" > omp_timing.csv
echo "N,Procs,Epochs,Time_s" > serial_timing.csv

python3 benchmark.py

echo ""
echo "============================================"
echo "  Step 4: Part I - Cluster Map"
echo "============================================"
cd "$SCRIPT_DIR/part1"
bash cluster_map.sh
python3 cluster_visualize.py

echo ""
echo "All done. Results are in: $RESULTS_DIR"
echo "Graphs: speedup_comparison.png, grid_scaling.png, efficiency.png,"
echo "        heatmap_mpi.png, heatmap_omp.png, node_availability.png"
