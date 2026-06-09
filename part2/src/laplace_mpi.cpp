#include <mpi.h>
#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <cstdlib>
#include <sstream>
#include <iomanip>

#define HOT_WALL  100.0
#define COLD_WALL 0.0

void initialize_grid(std::vector<double>& grid, int local_rows, int N,
                     int rank, int size) {
    grid.assign((local_rows + 2) * N, 0.0);
    if (rank == 0) {
        for (int j = 0; j < N; j++)
            grid[1*N + j] = HOT_WALL;
    }
    if (rank == size - 1) {
        for (int j = 0; j < N; j++)
            grid[local_rows*N + j] = COLD_WALL;
    }
}

double jacobi_step(const std::vector<double>& old_g,
                   std::vector<double>& new_g,
                   int local_rows, int N, int rank, int size) {
    double max_delta = 0.0;
    for (int i = 1; i <= local_rows; i++) {
        bool top_wall = (rank == 0 && i == 1);
        bool bot_wall = (rank == size-1 && i == local_rows);
        for (int j = 0; j < N; j++) {
            if (j == 0 || j == N-1 || top_wall || bot_wall) {
                new_g[i*N+j] = old_g[i*N+j];
                continue;
            }
            double nv = 0.25*(old_g[(i-1)*N+j]+old_g[(i+1)*N+j]+
                              old_g[i*N+(j-1)]+old_g[i*N+(j+1)]);
            double d = fabs(nv - old_g[i*N+j]);
            if (d > max_delta) max_delta = d;
            new_g[i*N+j] = nv;
        }
    }
    return max_delta;
}

void exchange_ghost_rows(std::vector<double>& grid, int local_rows,
                         int N, int rank, int size, MPI_Comm comm) {
    MPI_Status status;
    if (rank > 0)
        MPI_Sendrecv(&grid[1*N], N, MPI_DOUBLE, rank-1, 0,
                     &grid[0*N], N, MPI_DOUBLE, rank-1, 1, comm, &status);
    if (rank < size-1)
        MPI_Sendrecv(&grid[local_rows*N], N, MPI_DOUBLE, rank+1, 1,
                     &grid[(local_rows+1)*N], N, MPI_DOUBLE, rank+1, 0,
                     comm, &status);
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int N          = 256;
    int max_epochs = 5000;
    double tol     = 1e-4;
    if (argc >= 2) N          = atoi(argv[1]);
    if (argc >= 3) max_epochs = atoi(argv[2]);
    if (argc >= 4) tol        = atof(argv[3]);

    if (rank == 0)
        std::cout << "MPI Laplace: N=" << N << " procs=" << size << "\n";

    int base_rows  = N / size;
    int remainder  = N % size;
    int local_rows = base_rows + (rank < remainder ? 1 : 0);

    std::vector<int> recv_counts(size), displs(size);
    if (rank == 0) {
        int offset = 0;
        for (int r = 0; r < size; r++) {
            int rows_r = base_rows + (r < remainder ? 1 : 0);
            recv_counts[r] = rows_r * N;
            displs[r] = offset;
            offset += rows_r * N;
        }
    }

    std::vector<double> grid, new_grid;
    initialize_grid(grid, local_rows, N, rank, size);
    initialize_grid(new_grid, local_rows, N, rank, size);
    exchange_ghost_rows(grid, local_rows, N, rank, size, MPI_COMM_WORLD);

    MPI_Barrier(MPI_COMM_WORLD);
    double t_start = MPI_Wtime();

    int epoch = 0;
    double global_delta = tol + 1.0;
    while (epoch < max_epochs && global_delta > tol) {
        double local_delta = jacobi_step(grid, new_grid, local_rows, N, rank, size);
        MPI_Allreduce(&local_delta, &global_delta, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
        std::vector<double> tmp = grid;
        grid = new_grid;
        new_grid = tmp;
        exchange_ghost_rows(grid, local_rows, N, rank, size, MPI_COMM_WORLD);
        epoch++;
        if (rank == 0 && epoch % 500 == 0)
            std::cout << "  Epoch " << epoch << "  delta=" << global_delta << "\n";
    }

    MPI_Barrier(MPI_COMM_WORLD);
    double elapsed = MPI_Wtime() - t_start;

    if (rank == 0)
        std::cout << "Converged: " << epoch << " epochs, time=" << elapsed << " s\n";

    std::vector<double> local_real(local_rows * N);
    for (int i = 0; i < local_rows; i++)
        for (int j = 0; j < N; j++)
            local_real[i*N+j] = grid[(i+1)*N+j];

    std::vector<double> full_grid;
    if (rank == 0) full_grid.resize(N * N);

    MPI_Gatherv(&local_real[0], local_rows*N, MPI_DOUBLE,
                rank==0 ? &full_grid[0] : NULL,
                &recv_counts[0], &displs[0],
                MPI_DOUBLE, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        std::ostringstream oss;
        oss << "laplace_mpi_" << N << ".csv";
        std::ofstream out(oss.str().c_str());
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                out << full_grid[i*N+j];
                if (j < N-1) out << ",";
            }
            out << "\n";
        }
        std::cout << "Saved: " << oss.str() << "\n";

        std::ofstream timing("mpi_timing.csv", std::ios::app);
        timing << N << "," << size << "," << epoch << "," << elapsed << "\n";
    }

    MPI_Finalize();
    return 0;
}