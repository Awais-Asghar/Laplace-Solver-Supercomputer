# HPC Laplace Solver — Supercomputer Performance Analysis
![Project Status](https://img.shields.io/badge/status-Completed-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-NUST%20RCMS%20Supercomputer-blue.svg)
![CPU](https://img.shields.io/badge/CPU-AMD%20EPYC%207452-red.svg)
![MPI](https://img.shields.io/badge/Parallelism-MPI%20%7C%20OpenMP-orange.svg)
![Language](https://img.shields.io/badge/language-C%2B%2B-blue.svg)
![Build](https://img.shields.io/badge/build-CMake-064F8C.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

## Project Structure

```
HPC_Project/
├── part1/
│   ├── cluster_map.sh          # Maps all HPC nodes, ranks by availability
│   └── cluster_visualize.py    # Generates bar charts and heatmaps from CSV
│
├── part2/
│   ├── CMakeLists.txt          # Build system (finds MPI and OpenMP automatically)
│   ├── src/
│   │   ├── laplace_serial.cpp  # Single-threaded reference solver
│   │   ├── laplace_mpi.cpp     # MPI solver with ghost row exchange
│   │   ├── laplace_omp.cpp     # OpenMP solver for comparison
│   │   ├── verify_correctness.py # Compares MPI vs serial output
│   │   └── benchmark.py        # Runs all timing experiments, generates graphs
│   ├── build/                  # CMake build output goes here
│   └── results/                # Timing CSVs and PNG graphs go here
│
└── run_all.sh                  # One-shot script to build + run everything
```

---

## Setup (on HPC head node - afrit)

### Step 1: Transfer files to HPC

From Colab:
```bash
!sshpass -p 'awais@123' scp -r -oHostKeyAlgorithms=+ssh-rsa \
  -oStrictHostKeyChecking=no HPC_Project awais.seecs@10.19.10.50:~
```

From WSL/PC:
```bash
scp -r -oHostKeyAlgorithms=+ssh-rsa \
  -oStrictHostKeyChecking=no HPC_Project awais.seecs@10.19.10.50:~
```

### Step 2: SSH into HPC
```bash
ssh -oHostKeyAlgorithms=+ssh-rsa awais.seecs@10.19.10.50
```

### Step 3: Build
```bash
cd ~/HPC_Project/part2
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

### Step 4: Run Part I (Cluster Map)
```bash
cd ~/HPC_Project/part1
bash cluster_map.sh
python3 cluster_visualize.py
```

### Step 5: Run Part II (Laplace Solver)

**Correctness check (small grid, compare serial vs MPI):**
```bash
cd ~/HPC_Project/part2/results
./laplace_serial 32 10000 1e-4
mpirun -n 4 ./laplace_mpi 32 10000 1e-4
./laplace_omp 32 10000 1e-4 4
python3 verify_correctness.py 32
```

**Single run (N=256, 4 MPI procs):**
```bash
mpirun -n 4 ./laplace_mpi 256 5000 1e-4
```

**Run on a compute node (not head node):**
```bash
ssh compute-0-5   # pick an available node from Part I ranking
cd ~/HPC_Project/part2/results
mpirun -n 8 ./laplace_mpi 512 3000 1e-4
exit
```

**Full benchmark suite:**
```bash
python3 benchmark.py
```

---

## Arguments

All solvers accept: `[N] [max_epochs] [tolerance]`

| Binary          | Extra arg      | Example                              |
|-----------------|----------------|--------------------------------------|
| laplace_serial  | none           | `./laplace_serial 256 5000 1e-4`     |
| laplace_mpi     | none           | `mpirun -n 8 ./laplace_mpi 256 5000 1e-4` |
| laplace_omp     | [num_threads]  | `./laplace_omp 256 5000 1e-4 8`      |

---

## Algorithm Details (MPI)

1. The NxN grid is split ROW-WISE across MPI ranks.
2. Each rank owns `N/size` rows (remainder distributed across first few ranks).
3. Each rank allocates 2 extra ghost rows (one at top, one at bottom).
4. Every Jacobi iteration, each rank computes new values for its real rows.
5. Then MPI_Sendrecv exchanges boundary rows with neighboring ranks.
6. Convergence is checked globally using MPI_Allreduce (max of all local deltas).
7. Final solution is gathered to rank 0 using MPI_Gatherv.

**Boundary Conditions:**
- Top wall: 100 deg (hot)
- Bottom wall: 0 deg (cold)
- Left/Right walls: 0 (insulated)

---

## Output Files

| File                    | Description                        |
|-------------------------|------------------------------------|
| cluster_report.txt      | Text report of all nodes           |
| cluster_data.csv        | Node metrics in CSV format         |
| node_availability.png   | Bar chart of node scores           |
| node_load.png           | CPU and load average chart         |
| node_ram.png            | RAM usage per node                 |
| laplace_mpi_N.csv       | Solution grid (MPI, size N)        |
| laplace_omp_N.csv       | Solution grid (OpenMP, size N)     |
| laplace_serial_N.csv    | Solution grid (serial, size N)     |
| mpi_timing.csv          | Timing data for MPI runs           |
| omp_timing.csv          | Timing data for OpenMP runs        |
| speedup_comparison.png  | Speedup graph: MPI vs OpenMP       |
| grid_scaling.png        | Time vs grid size (log-log)        |
| efficiency.png          | Parallel efficiency                |
| heatmap_mpi.png         | Temperature field visualization    |

---

## Important Notes

- Do NOT run heavy simulations on the head node (afrit). Use compute nodes.
- Keep RAM usage in check. For N=1024, each grid = 8 MB. With MPI overhead,
  stay within the node's free RAM seen in Part I.
- For larger grids (N >= 512), increase max_epochs to at least 5000.
- Convergence gets slower as N increases (more cells to equilibrate).
