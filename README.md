# HPC Laplace Solver: Supercomputer Performance Analysis
![Project Status](https://img.shields.io/badge/status-DONE-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Supercomputer-blue.svg)
![CPU](https://img.shields.io/badge/CPU-AMD%20EPYC%207452-red.svg)
![MPI](https://img.shields.io/badge/Parallelism-MPI%20%7C%20OpenMP-orange.svg)
![Language](https://img.shields.io/badge/language-C%2B%2B-blue.svg)
![Build](https://img.shields.io/badge/build-CMake-064F8C.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/f4074a17-e80d-4a35-b063-cc557f044f3d" />

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/448265c3-58d0-4b5b-9cd4-d11c9e723086" />

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/adb591a0-398f-4b31-a816-758730d0cf50" />

## Project Structure

```
HPC_Project/
├── part1/
│   ├── cluster_map.sh
│   └── cluster_visualize.py
│
├── part2/
│   ├── CMakeLists.txt
│   ├── src/
│   │   ├── laplace_serial.cpp
│   │   ├── laplace_mpi.cpp
│   │   ├── laplace_omp.cpp
│   │   ├── verify_correctness.py
│   │   └── benchmark.py
│   ├── build/
│   └── results/
│
└── run_all.sh
```

## Methodology 

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/aeee367b-04df-4c85-9a4b-411ec9449eca" />

## Step-by-Step Execution Guide

### Phase 1: Upload the Project to HPC

#### Step 1.1:  Open Your Terminal

Open WSL on your Windows PC inside the project folder, or use a Linux terminal.

#### Step 1.2:  Upload the Project Folder to HPC

For a temporary user account:
```bash
scp -r -O -oHostKeyAlgorithms=ssh-rsa Project user2@10.19.10.50:~
```

For your own named account:
```bash
rsync -avz --progress -e "ssh -p 22 -oHostKeyAlgorithms=+ssh-rsa" . awais.seecs@10.19.10.150:~/Solution
```

> Enter your HPC password when prompted.


### Phase 2: Log Into the HPC

#### Step 2.1: SSH Into the HPC Head Node

For a temporary user account:
```bash
ssh -X user2@10.19.10.50 -oHostKeyAlgorithms=+ssh-rsa
ls
```

For your own named account:
```bash
ssh -X awais.seecs@10.19.10.150 -p 22 -oHostKeyAlgorithms=+ssh-rsa
ls
```

> **WARNING:** Never run simulations on the head node (afrit). Any simulation
> on the head node will be terminated without warning and data may be lost.

#### Step 2.2: Navigate to the Build Folder

```bash
cd Solution
ls
cd Project
ls
cd part2
ls
cd build
ls
```

#### Step 2.3:  Build the Project Using CMake

```bash
cmake ..
```

#### Step 2.4: Compile All Three Solvers

```bash
make -j4
```

#### Step 2.5: Verify Binaries Were Created

```bash
ls
```

You should see `laplace_mpi`, `laplace_omp`, and `laplace_serial` listed.


### Phase 3: Set Up the Results Folder

#### Step 3.1: Create the Results Directory

```bash
mkdir -p ~/Project/part2/results
```

#### Step 3.2: Copy Binaries and Scripts Into Results

```bash
cp ./laplace_mpi     ~/Project/part2/results/
cp ./laplace_omp     ~/Project/part2/results/
cp ./laplace_serial  ~/Project/part2/results/
cp ../src/verify_correctness.py ~/Project/part2/results/
cp ../src/benchmark.py          ~/Project/part2/results/
```

#### Step 3.3: Confirm Everything Is in Place

```bash
cd ..
ls -lh ~/Project/part2/results/
```

Expected files: `benchmark.py` `laplace_mpi` `laplace_omp` `laplace_serial` `verify_correctness.py`


### Phase 4: Initial Test Run (Small Grid)

Navigate to the results folder and run a correctness check on a small grid
before the full benchmark. Check which Python version is on your HPC first.

```bash
cd ~/Project/part2/results

./laplace_serial 32 10000 1e-4

mpirun -n 4 ./laplace_mpi 32 10000 1e-4

./laplace_omp 32 10000 1e-4 4

python3 verify_correctness.py 32
```

Expected output for each comparison:
```
RESULT: PASS - outputs match within tolerance.
```

### Phase 5: Full Benchmark

Run each command one at a time. Wait for each to finish before typing the next.

#### Step 5.1: MPI Scaling Test (N=256, Varying Processes)

```bash
mpirun -n 1 ./laplace_mpi 256 5000 1e-4
mpirun -n 2 ./laplace_mpi 256 5000 1e-4
mpirun -n 4 ./laplace_mpi 256 5000 1e-4
mpirun -n 8 ./laplace_mpi 256 5000 1e-4
```

#### Step 5.2: OpenMP Scaling Test (N=256, Varying Threads)

```bash
./laplace_omp 256 5000 1e-4 1
./laplace_omp 256 5000 1e-4 2
./laplace_omp 256 5000 1e-4 4
./laplace_omp 256 5000 1e-4 8
```

#### Step 5.3: Serial Baseline for Different Grid Sizes

```bash
./laplace_serial 256 5000 1e-4
./laplace_serial 512 5000 1e-4
```

#### Step 5.4: Grid Size Scaling With 4 Procs and 4 Threads

```bash
mpirun -n 4 ./laplace_mpi 128 5000 1e-4
mpirun -n 4 ./laplace_mpi 256 5000 1e-4
mpirun -n 4 ./laplace_mpi 512 5000 1e-4

./laplace_omp 128 5000 1e-4 4
./laplace_omp 256 5000 1e-4 4
./laplace_omp 512 5000 1e-4 4
```

### Phase 6: Generate Graphs

#### Step 6.1: Print the CSV Contents

```bash
cat mpi_timing.csv
cat omp_timing.csv
cat serial_timing.csv
```

#### Step 6.2: Install matplotlib on Your PC

```bash
pip install matplotlib numpy
```

#### Step 6.3: Generate All Performance Graphs

```bash
python3 benchmark.py
```

Graphs produced:

| File | Description |
|------|-------------|
| `speedup_comparison.png` | MPI vs OpenMP speedup line chart |
| `execution_time.png` | Execution time vs parallelism |
| `grid_scaling.png` | Time vs grid size (log-log) |
| `efficiency.png` | Parallel efficiency percentage |
| `bar_comparison.png` | Serial vs OpenMP vs MPI at N=256 |
| `mpi_scaling.png` | MPI execution time per process count |

### Phase 7: Part I | Mapping the HPC Cluster

#### Step 7.1: SSH Back Into HPC and Go to Part 1 Folder

```bash
ssh -X awais.seecs@10.19.10.150 -p 22 -oHostKeyAlgorithms=+ssh-rsa
cd ~/Project/part1
```

#### Step 7.2: Run the Cluster Mapping Script

```bash
bash cluster_map.sh
```

> Takes 2 to 4 minutes as it probes 29 nodes. Two files are created:
> - `cluster_report.txt` — human readable ranking table
> - `cluster_data.csv` — comma separated data for graph generation

#### Step 7.3: View the Node Ranking

```bash
cat cluster_report.txt
```

#### Step 7.4: Cluster Graphs Produced

| File | Description |
|------|-------------|
| `node_availability.png` | Bar chart of node availability scores |
| `node_ram.png` | RAM usage per node |
| `node_cpu_specs.png` | CPU specification chart |
| `numa_architecture.png` | NUMA topology diagram |
| `ram_pie.png` | RAM distribution pie chart |

## Solver Arguments

All solvers accept: `[N] [max_epochs] [tolerance]`

| Binary | Extra Arg | Example |
|--------|-----------|---------|
| `laplace_serial` | none | `./laplace_serial 256 5000 1e-4` |
| `laplace_mpi` | none | `mpirun -n 8 ./laplace_mpi 256 5000 1e-4` |
| `laplace_omp` | `[num_threads]` | `./laplace_omp 256 5000 1e-4 8` |

## Algorithm Details (MPI)

1. The NxN grid is split row-wise across MPI ranks.
2. Each rank owns `N/size` rows (remainder distributed across first few ranks).
3. Each rank allocates 2 extra ghost rows (top and bottom).
4. Every Jacobi iteration, each rank computes new values for its real rows.
5. `MPI_Sendrecv` exchanges boundary rows with neighboring ranks.
6. Convergence checked globally using `MPI_Allreduce` (max of all local deltas).
7. Final solution gathered to rank 0 using `MPI_Gatherv`.

**Boundary Conditions:**

| Wall | Temperature |
|------|-------------|
| Top | 100 deg C (HOT) |
| Bottom | 0 deg C (COLD) |
| Left / Right | 0 deg C (Insulated) |

## Results

### MPI Scaling
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/d9fed1d7-0daa-4a14-93a8-e60f506db071" />

### OpenMP Scaling
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/31dc58a5-3c80-4fcb-87c6-6da6deaa427c" />

### MPI vs OpenMP Head-to-Head
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/1b2d289e-e274-4b12-a5c0-1a982879dbf0" />

### Grid Size Scaling
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/15f82968-6cc6-4cab-b00f-512e75124171" />

### Verification and Correctness
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/83da12e5-8803-4cb7-bd23-2f4e5b0c0dc3" />

### Parallel Efficiency
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/cb8e54de-c857-4b34-a689-c5d946f6bcb6" />

## Performance Results Summary

### MPI Scaling (N=256, 5000 epochs)

| MPI Processes | Time (s) | Speedup | Efficiency (%) |
|---------------|----------|---------|----------------|
| 1 | 1.466 | 1.00x | 100.0 |
| 2 | 0.911 | 1.61x | 80.5 |
| 4 | 0.538 | 2.72x | 68.1 |
| 8 | 0.479 | 3.06x | 38.3 |

### OpenMP Scaling (N=256, 5000 epochs)

| OMP Threads | Time (s) | Speedup | Efficiency (%) |
|-------------|----------|---------|----------------|
| 1 | 0.997 | 1.00x | 100.0 |
| 2 | 0.959 | 1.04x | 52.0 |
| 4 | 1.253 | 0.80x | 19.9 |
| 8 | 1.790 | 0.56x | 6.9 |

### Grid Size Scaling (4 procs / 4 threads, 5000 epochs)

| Grid Size | Serial (s) | MPI 4P (s) | OMP 4T (s) | MPI vs Serial |
|-----------|------------|------------|------------|---------------|
| 128x128 | N/A | 0.218 | 0.368 | N/A |
| 256x256 | 1.895 | 0.538 | 1.253 | 3.52x |
| 512x512 | 5.346 | 1.782 | 4.667 | 3.00x |

## Key Findings

- **MPI** achieves 3.06x speedup at 8 processes with consistent scaling.
- **OpenMP** degrades beyond 2 threads due to NUMA effects on the AMD EPYC 7452 dual-socket machine.
- **MPI** is the superior model for this memory-bandwidth-bound problem on NUMA hardware.
- All three solvers produce **bit-for-bit identical results** verified with 0.0 max absolute difference.
- Primary MPI bottleneck is ghost row communication overhead at high process counts.
- For N=512, more than 5000 epochs are needed for full convergence — consider SOR or multigrid.


<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/8a54a2b9-237d-4363-9cac-869cf9344a40" />

## Output Files Reference

| File | Description |
|------|-------------|
| `cluster_report.txt` | Text report of all nodes |
| `cluster_data.csv` | Node metrics in CSV format |
| `laplace_mpi_N.csv` | MPI solution grid for size N |
| `laplace_omp_N.csv` | OpenMP solution grid for size N |
| `laplace_serial_N.csv` | Serial solution grid for size N |
| `mpi_timing.csv` | Timing data for all MPI runs |
| `omp_timing.csv` | Timing data for all OpenMP runs |
| `serial_timing.csv` | Timing data for all serial runs |


## Important Notes

- Do NOT run heavy simulations on the head node (afrit). Use compute nodes.
- For N=1024, each grid takes ~8 MB. Stay within the free RAM shown in Part I.
- For grids N >= 512, set max_epochs to at least 5000.
- Convergence gets slower as N increases (more cells to equilibrate).
- Offline nodes from the cluster scan: `compute-0-7, 14, 15, 20, 25, 29, 30`.

## HPC System Info

| Field | Value |
|-------|-------|
| Head Node | afrit |
| IP Address | 10.19.10.150 |
| CPU | AMD EPYC 7452 32-Core |
| Total CPUs | 128 (2 sockets x 32 cores x 2 threads) |
| Total RAM | 125 GB |
| Compute Nodes | 29 (all offline during this project) |
| MPI Version | OpenMPI 3.1 |
| OpenMP Version | 4.5 |
| Compiler | GCC 8.5.0 |

## Conclusion
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/4715ff52-8ba7-49e5-b9b0-c4d153a7ce34" />
