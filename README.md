<img width="1988" height="590" alt="banner" src="https://github.com/user-attachments/assets/9d21b3f5-78f2-4442-82cd-43711e036f7b" />

Parallel 2D Laplace solver implemented using **MPI** and **OpenMP** on the **NUST RCMS Supercomputer**. The project benchmarks distributed memory vs shared memory parallelism using the Jacobi iterative method on a 2D heat diffusion problem, with full performance analysis, graphs, and correctness verification.

---

## Problem Statement

Solve the 2D Laplace equation (steady-state heat diffusion) on an N x N grid:

```
∇²u = 0
```

Boundary conditions:
- Top wall: 100°C (hot)
- Bottom wall: 0°C (cold)
- Left and right walls: 0°C (insulated)

Solved iteratively using the **Jacobi method** until convergence (max delta < 1e-4) or a maximum epoch limit is reached.

---

## Tools and Technologies

| Tool / Technology | Purpose |
|---|---|
| **C++** (C++03 compatible) | Core solver implementation |
| **MPI (OpenMPI)** | Distributed memory parallelism across processes |
| **OpenMP** | Shared memory parallelism across threads |
| **CMake 2.8** | Build system (compatible with GCC 4.4.7) |
| **GCC 4.4.7** | Compiler on NUST RCMS HPC |
| **Python 3** | Benchmarking, correctness verification, graph generation |
| **Matplotlib** | Performance graphs |
| **NUST RCMS Supercomputer** | AMD EPYC 7452, 128 CPUs, 125 GB RAM |
| **MPI_Sendrecv** | Ghost row exchange between MPI processes |
| **MPI_Allreduce** | Global convergence check across all processes |
| **MPI_Gatherv** | Collecting distributed results to rank 0 |

---

## Project Structure

```
Project/
├── part1/
│   ├── cluster_map.sh          # Scans all HPC compute nodes and ranks by availability
│   ├── cluster_visualize.py    # Generates node availability, CPU, and RAM graphs
│   ├── cluster_data.csv        # Raw cluster data output
│   └── cluster_report.txt      # Human-readable node ranking report
│
└── part2/
    ├── CMakeLists.txt           # CMake build configuration
    ├── src/
    │   ├── laplace_serial.cpp   # Serial reference implementation
    │   ├── laplace_mpi.cpp      # MPI parallel solver
    │   ├── laplace_omp.cpp      # OpenMP parallel solver
    │   ├── verify_correctness.py# Compares solver outputs for correctness
    │   └── benchmark.py         # Runs benchmarks and generates performance graphs
    └── results/
        ├── *.csv                # Timing and solver output data
        └── *.png                # Generated performance graphs
```

## HPC Cluster Info (Part I)

| Attribute | Details |
|---|---|
| Head Node | master (AMD EPYC 7452) |
| Total CPUs | 128 (2 sockets x 32 cores x 2 threads) |
| Total RAM | 125 GB |
| Compute Nodes | compute-0-0 to compute-0-28 (29 nodes) |
| Offline Nodes | 7, 14, 15, 20, 25, 29, 30 |

---

## License

This project is licensed under the MIT License.
