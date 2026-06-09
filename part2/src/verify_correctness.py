import sys
import math

def load_csv(fname):
    data = []
    f = open(fname, 'r')
    for line in f:
        row = [float(x) for x in line.strip().split(',')]
        data.append(row)
    f.close()
    return data

def verify(serial_file, mpi_file, atol=1e-2):
    print("\nComparing:\n  " + serial_file + "\n  " + mpi_file)
    try:
        A = load_csv(serial_file)
        B = load_csv(mpi_file)
    except Exception as e:
        print("ERROR loading files: " + str(e))
        return False

    if len(A) != len(B) or len(A[0]) != len(B[0]):
        print("SHAPE MISMATCH")
        return False

    max_diff  = 0.0
    mean_diff = 0.0
    count = 0
    for i in range(len(A)):
        for j in range(len(A[0])):
            d = abs(A[i][j] - B[i][j])
            if d > max_diff:
                max_diff = d
            mean_diff += d
            count += 1
    mean_diff = mean_diff / count

    print("Max absolute difference : " + str(max_diff))
    print("Mean absolute difference: " + str(mean_diff))
    print("Tolerance               : " + str(atol))

    if max_diff < atol:
        print("RESULT: PASS - outputs match within tolerance.")
        return True
    else:
        print("RESULT: FAIL - difference exceeds tolerance.")
        return False

N    = sys.argv[1] if len(sys.argv) > 1 else "32"
atol = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-2

serial = "laplace_serial_" + N + ".csv"
mpi    = "laplace_mpi_"    + N + ".csv"
omp    = "laplace_omp_"    + N + ".csv"

ok1 = verify(serial, mpi,  atol)
ok2 = verify(serial, omp,  atol)

if ok1 and ok2:
    sys.exit(0)
else:
    sys.exit(1)