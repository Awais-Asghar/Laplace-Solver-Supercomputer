#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <cstdlib>
#include <ctime>
#include <sstream>

#define HOT_WALL  100.0
#define COLD_WALL 0.0

void initialize_grid(std::vector<double>& grid, int N) {
    grid.assign(N * N, 0.0);
    for (int j = 0; j < N; j++) grid[0*N + j]     = HOT_WALL;
    for (int j = 0; j < N; j++) grid[(N-1)*N + j]  = COLD_WALL;
}

int main(int argc, char* argv[]) {
    int N          = 32;
    int max_epochs = 10000;
    double tol     = 1e-4;

    if (argc >= 2) N          = atoi(argv[1]);
    if (argc >= 3) max_epochs = atoi(argv[2]);
    if (argc >= 4) tol        = atof(argv[3]);

    std::cout << "Serial Laplace Solver: N=" << N << "\n";

    std::vector<double> grid, new_grid;
    initialize_grid(grid, N);
    initialize_grid(new_grid, N);
    for (int j = 0; j < N; j++) {
        new_grid[0*N+j]     = HOT_WALL;
        new_grid[(N-1)*N+j] = COLD_WALL;
    }

    struct timespec ts, te;
    clock_gettime(CLOCK_MONOTONIC, &ts);

    int epoch = 0;
    double delta = tol + 1.0;
    while (epoch < max_epochs && delta > tol) {
        delta = 0.0;
        for (int i = 1; i < N-1; i++) {
            for (int j = 1; j < N-1; j++) {
                double nv = 0.25*(grid[(i-1)*N+j]+grid[(i+1)*N+j]+
                                  grid[i*N+(j-1)]+grid[i*N+(j+1)]);
                double d  = fabs(nv - grid[i*N+j]);
                if (d > delta) delta = d;
                new_grid[i*N+j] = nv;
            }
        }
        std::vector<double> tmp = grid;
        grid = new_grid;
        new_grid = tmp;
        epoch++;
    }

    clock_gettime(CLOCK_MONOTONIC, &te);
    double elapsed = (te.tv_sec - ts.tv_sec) + (te.tv_nsec - ts.tv_nsec)*1e-9;

    std::cout << "Converged: " << epoch << " epochs, delta=" << delta
              << ", time=" << elapsed << " s\n";

    std::ostringstream oss;
    oss << "laplace_serial_" << N << ".csv";
    std::ofstream out(oss.str().c_str());
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            out << grid[i*N+j];
            if (j < N-1) out << ",";
        }
        out << "\n";
    }
    std::cout << "Saved: " << oss.str() << "\n";

    std::ofstream timing("serial_timing.csv", std::ios::app);
    timing << N << ",1," << epoch << "," << elapsed << "\n";

    return 0;
}