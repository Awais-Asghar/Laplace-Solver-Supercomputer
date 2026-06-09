#!/usr/bin/env python3
"""
Part II: Performance Benchmark and Graph Generation
Runs the MPI and OpenMP solvers across multiple grid sizes and process counts,
then generates comparison plots.

Run this script on the HPC after compiling both binaries.
"""

import subprocess
import os
import sys
import csv
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- Configuration ----
MPI_BIN    = "./laplace_mpi"
OMP_BIN    = "./laplace_omp"
SERIAL_BIN = "./laplace_serial"

# Grid sizes to benchmark (NxN)
GRID_SIZES = [64, 128, 256, 512, 1024]

# MPI process counts
MPI_PROCS = [1, 2, 4, 8, 16]

# OpenMP thread counts
OMP_THREADS = [1, 2, 4, 8, 16]

MAX_EPOCHS = 3000
TOL = "1e-4"

# ---- Run a command and return stdout ----
def run(cmd, timeout=600):
    print(f"  Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            print(f"  STDERR: {result.stderr[:300]}")
        return result.stdout
    except subprocess.TimeoutExpired:
        print("  TIMEOUT!")
        return ""
    except Exception as e:
        print(f"  ERROR: {e}")
        return ""

def parse_time(output):
    """Extract elapsed time from solver output."""
    for line in output.splitlines():
        if "Time elapsed" in line:
            try:
                return float(line.split()[-2])
            except:
                pass
    return None

def parse_epochs(output):
    for line in output.splitlines():
        if "Converged after" in line:
            try:
                return int(line.split()[2])
            except:
                pass
    return None

# ---- Benchmark 1: MPI scaling (fixed grid, varying procs) ----
def bench_mpi_scaling():
    print("\n[1] MPI Scaling Benchmark (N=256, varying MPI procs)")
    results = []
    N = 256
    for np_ in MPI_PROCS:
        out = run(["mpirun", "-n", str(np_), MPI_BIN, str(N), str(MAX_EPOCHS), TOL])
        t = parse_time(out)
        e = parse_epochs(out)
        if t:
            print(f"    procs={np_:3d}  time={t:.4f}s  epochs={e}")
            results.append((np_, t, e))
        else:
            print(f"    procs={np_:3d}  FAILED")
    return results

# ---- Benchmark 2: OpenMP scaling (fixed grid, varying threads) ----
def bench_omp_scaling():
    print("\n[2] OpenMP Scaling Benchmark (N=256, varying threads)")
    results = []
    N = 256
    for nt in OMP_THREADS:
        env = os.environ.copy()
        env["OMP_NUM_THREADS"] = str(nt)
        out = run([OMP_BIN, str(N), str(MAX_EPOCHS), TOL, str(nt)])
        t = parse_time(out)
        e = parse_epochs(out)
        if t:
            print(f"    threads={nt:3d}  time={t:.4f}s  epochs={e}")
            results.append((nt, t, e))
        else:
            print(f"    threads={nt:3d}  FAILED")
    return results

# ---- Benchmark 3: Grid size scaling ----
def bench_grid_scaling():
    print("\n[3] Grid Size Scaling Benchmark (4 procs/threads)")
    mpi_results, omp_results, serial_results = [], [], []
    for N in GRID_SIZES:
        # Serial
        out = run([SERIAL_BIN, str(N), str(MAX_EPOCHS), TOL])
        t = parse_time(out)
        if t: serial_results.append((N, t))

        # MPI (4 procs)
        out = run(["mpirun", "-n", "4", MPI_BIN, str(N), str(MAX_EPOCHS), TOL])
        t = parse_time(out)
        if t: mpi_results.append((N, t))

        # OpenMP (4 threads)
        out = run([OMP_BIN, str(N), str(MAX_EPOCHS), TOL, "4"])
        t = parse_time(out)
        if t: omp_results.append((N, t))

        print(f"    N={N}: serial={serial_results[-1][1] if serial_results else 'N/A':.3f}s "
              f"mpi={mpi_results[-1][1] if mpi_results else 'N/A':.3f}s "
              f"omp={omp_results[-1][1] if omp_results else 'N/A':.3f}s")

    return serial_results, mpi_results, omp_results

# ---- Plot 1: Speedup vs Processes/Threads ----
def plot_speedup(mpi_results, omp_results):
    if not mpi_results or not omp_results:
        print("Skipping speedup plot (no data)")
        return

    t_serial_mpi = mpi_results[0][1]   # time with 1 MPI proc = baseline
    t_serial_omp = omp_results[0][1]   # time with 1 OMP thread = baseline

    mpi_procs   = [r[0] for r in mpi_results]
    mpi_speedup = [t_serial_mpi / r[1] for r in mpi_results]
    omp_threads = [r[0] for r in omp_results]
    omp_speedup = [t_serial_omp / r[1] for r in omp_results]

    ideal_x = list(range(1, max(max(mpi_procs), max(omp_threads)) + 1))
    ideal_y = ideal_x

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(mpi_procs,   mpi_speedup, 'b-o', label='MPI (N=256)', linewidth=2)
    ax.plot(omp_threads, omp_speedup, 'r-s', label='OpenMP (N=256)', linewidth=2)
    ax.plot(ideal_x, ideal_y, 'k--', label='Ideal Linear Speedup', alpha=0.5)
    ax.set_xlabel("Number of Processes / Threads")
    ax.set_ylabel("Speedup")
    ax.set_title("Speedup: MPI vs OpenMP (Laplace Solver, N=256)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("speedup_comparison.png", dpi=150)
    print("Saved: speedup_comparison.png")
    plt.close()

# ---- Plot 2: Time vs Grid Size ----
def plot_grid_scaling(serial_results, mpi_results, omp_results):
    fig, ax = plt.subplots(figsize=(8, 5))

    if serial_results:
        Ns, ts = zip(*serial_results)
        ax.loglog(Ns, ts, 'k-o', label='Serial', linewidth=2)
    if mpi_results:
        Ns, ts = zip(*mpi_results)
        ax.loglog(Ns, ts, 'b-o', label='MPI (4 procs)', linewidth=2)
    if omp_results:
        Ns, ts = zip(*omp_results)
        ax.loglog(Ns, ts, 'r-s', label='OpenMP (4 threads)', linewidth=2)

    ax.set_xlabel("Grid Size N (NxN grid)")
    ax.set_ylabel("Time (s) [log scale]")
    ax.set_title("Performance vs Grid Size (Laplace Solver)")
    ax.legend()
    ax.grid(True, which='both', alpha=0.3)
    plt.tight_layout()
    plt.savefig("grid_scaling.png", dpi=150)
    print("Saved: grid_scaling.png")
    plt.close()

# ---- Plot 3: Efficiency ----
def plot_efficiency(mpi_results, omp_results):
    if not mpi_results or not omp_results:
        return

    t1_mpi = mpi_results[0][1]
    t1_omp = omp_results[0][1]

    mpi_procs = [r[0] for r in mpi_results]
    mpi_eff   = [t1_mpi / (r[0] * r[1]) * 100 for r in mpi_results]
    omp_thr   = [r[0] for r in omp_results]
    omp_eff   = [t1_omp / (r[0] * r[1]) * 100 for r in omp_results]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(mpi_procs, mpi_eff, 'b-o', label='MPI Efficiency', linewidth=2)
    ax.plot(omp_thr,   omp_eff, 'r-s', label='OpenMP Efficiency', linewidth=2)
    ax.axhline(100, color='k', linestyle='--', alpha=0.5, label='Ideal (100%)')
    ax.set_xlabel("Processes / Threads")
    ax.set_ylabel("Parallel Efficiency (%)")
    ax.set_title("Parallel Efficiency: MPI vs OpenMP")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 120)
    plt.tight_layout()
    plt.savefig("efficiency.png", dpi=150)
    print("Saved: efficiency.png")
    plt.close()

# ---- Plot 4: Solution Heatmap ----
def plot_heatmap(csv_file, title, out_file):
    try:
        import numpy as np
        grid = np.loadtxt(csv_file, delimiter=',')
        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(grid, cmap='hot', origin='upper',
                       vmin=0, vmax=100, aspect='auto')
        plt.colorbar(im, ax=ax, label='Temperature')
        ax.set_title(title)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        plt.tight_layout()
        plt.savefig(out_file, dpi=150)
        print(f"Saved: {out_file}")
        plt.close()
    except Exception as e:
        print(f"Could not plot heatmap: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("  HPC Laplace Solver Benchmark Suite")
    print("=" * 50)

    mpi_scale  = bench_mpi_scaling()
    omp_scale  = bench_omp_scaling()
    serial_gs, mpi_gs, omp_gs = bench_grid_scaling()

    print("\nGenerating plots...")
    plot_speedup(mpi_scale, omp_scale)
    plot_grid_scaling(serial_gs, mpi_gs, omp_gs)
    plot_efficiency(mpi_scale, omp_scale)

    # Heatmap of solution (if file exists)
    plot_heatmap("laplace_mpi_256.csv",    "Laplace Solution (MPI, N=256)",    "heatmap_mpi.png")
    plot_heatmap("laplace_omp_256.csv",    "Laplace Solution (OpenMP, N=256)", "heatmap_omp.png")
    plot_heatmap("laplace_serial_256.csv", "Laplace Solution (Serial, N=256)", "heatmap_serial.png")

    print("\nAll benchmarks complete.")
