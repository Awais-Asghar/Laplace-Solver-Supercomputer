#include <omp.h>
#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <cstdlib>
#include <sstream>

#define HOT_WALL  100.0
#define COLD_WALL 0.0

void initialize_grid(std::vector<double>& grid, int N) {
    grid.assign(N * N, 0.0);
    for (int j = 0; j < N; j++) grid[0*N + j]    = HOT_WALL;
    for (int j = 0; j < N; j++) grid[(N-1)*N + j] = COLD_WALL;
}

int main(int argc, char* argv[]) {
    int N           = 256;
    int max_epochs  = 5000;
    double tol      = 1e-4;
    int num_threads = omp_get_max_threads();

    if (argc >= 2) N           = atoi(argv[1]);
    if (argc >= 3) max_epochs  = atoi(argv[2]);
    if (argc >= 4) tol         = atof(argv[3]);
    if (argc >= 5) num_threads = atoi(argv[4]);

    std::cout << "OpenMP Laplace: N=" << N << " threads=" << num_threads << "\n";

    std::vector<double> grid, new_grid;
    initialize_grid(grid, N);
    initialize_grid(new_grid, N);
    for (int j = 0; j < N; j++) {
        new_grid[0*N+j]     = HOT_WALL;
        new_grid[(N-1)*N+j] = COLD_WALL;
    }

    double t_start = omp_get_wtime();

    int epoch = 0;
    double delta = tol + 1.0;

    std::vector<double> thread_max(num_threads, 0.0);

    while (epoch < max_epochs && delta > tol) {

        for (int t = 0; t < num_threads; t++) thread_max[t] = 0.0;

        #pragma omp parallel num_threads(num_threads)
        {
            int tid = omp_get_thread_num();
            double local_max = 0.0;

            #pragma omp for schedule(static)
            for (int i = 1; i < N-1; i++) {
                for (int j = 1; j < N-1; j++) {
                    double nv = 0.25*(grid[(i-1)*N+j]+grid[(i+1)*N+j]+
                                      grid[i*N+(j-1)]+grid[i*N+(j+1)]);
                    double d = fabs(nv - grid[i*N+j]);
                    if (d > local_max) local_max = d;
                    new_grid[i*N+j] = nv;
                }
            }
            thread_max[tid] = local_max;
        }

        delta = 0.0;
        for (int t = 0; t < num_threads; t++)
            if (thread_max[t] > delta) delta = thread_max[t];

        std::vector<double> tmp = grid;
        grid = new_grid;
        new_grid = tmp;
        epoch++;

        if (epoch % 500 == 0)
            std::cout << "  Epoch " << epoch << "  delta=" << delta << "\n";
    }

    double elapsed = omp_get_wtime() - t_start;
    std::cout << "Converged: " << epoch << " epochs, time=" << elapsed << " s\n";

    std::ostringstream oss;
    oss << "laplace_omp_" << N << ".csv";
    std::ofstream out(oss.str().c_str());
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            out << grid[i*N+j];
            if (j < N-1) out << ",";
        }
        out << "\n";
    }
    std::cout << "Saved: " << oss.str() << "\n";

    std::ofstream timing("omp_timing.csv", std::ios::app);
    timing << N << "," << num_threads << "," << epoch << "," << elapsed << "\n";

    return 0;
}