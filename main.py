"""
The implementation of this Sudoku solver is based on the paper:

    "A SAT-based Sudoku solver" by Tjark Weber

    https://www.lri.fr/~conchon/mpri/weber.pdf

If you want to understand the code below, in particular the function valid(),
which calculates the 324 clauses corresponding to 9 cells, you are strongly
encouraged to read the paper first.  The paper is very short, but contains
all necessary information.
"""
import pycosat
import time
import numpy
import random
import matplotlib.pyplot as plt

solve_time = numpy.zeros(82)
solve_times = []
single_solve_count = 1
iteration_count = 1000


def v(i, j, d):
    """
    Return the number of the variable of cell i, j and digit d,
    which is an integer in the range of 1 to 729 (including).
    """
    return 81 * (i - 1) + 9 * (j - 1) + d


def sudoku_clauses():
    """
    Create the (11745) Sudoku clauses, and return them as a list.
    Note that these clauses are *independent* of the particular
    Sudoku puzzle at hand.
    """
    res = []
    # for all cells, ensure that the each cell:
    for i in range(1, 10):
        for j in range(1, 10):
            # denotes (at least) one of the 9 digits (1 clause)
            res.append([v(i, j, d) for d in range(1, 10)])
            # does not denote two different digits at once (36 clauses)
            for d in range(1, 10):
                for dp in range(d + 1, 10):
                    res.append([-v(i, j, d), -v(i, j, dp)])

    def valid(cells):
        # Append 324 clauses, corresponding to 9 cells, to the result.
        # The 9 cells are represented by a list tuples.  The new clauses
        # ensure that the cells contain distinct values.
        for i, xi in enumerate(cells):
            for j, xj in enumerate(cells):
                if i < j:
                    for d in range(1, 10):
                        res.append([-v(xi[0], xi[1], d), -v(xj[0], xj[1], d)])

    # ensure rows and columns have distinct values
    for i in range(1, 10):
        valid([(i, j) for j in range(1, 10)])
        valid([(j, i) for j in range(1, 10)])
    # ensure 3x3 sub-grids "regions" have distinct values
    for i in 1, 4, 7:
        for j in 1, 4, 7:
            valid([(i + k % 3, j + k // 3) for k in range(9)])

    assert len(res) == 81 * (1 + 36) + 27 * 324
    return res


def solve(grid, current_number):
    """
    solve a Sudoku grid inplace
    """
    clauses = sudoku_clauses()
    for i in range(1, 10):
        for j in range(1, 10):
            d = grid[i - 1][j - 1]
            # For each digit already known, a clause (with one literal).
            # Note:
            #     We could also remove all variables for the known cells
            #     altogether (which would be more efficient).  However, for
            #     the sake of simplicity, we decided not to do that.
            if d:
                clauses.append([v(i, j, d)])

    # solve the SAT problem
    start = time.time()
    for m in range(single_solve_count):
        sol = pycosat.solve(clauses)
    end = time.time()
    solve_times.append(end - start)
    solve_time[current_number] += (end - start)
    """proper = is_proper(clauses)
    solve_times.append(proper)
    solve_time[current_number] += proper
    sol = set(pycosat.solve(clauses))"""

    # if proper:
    def read_cell(i, j):
        # return the digit of cell i, j according to the solution
        for d in range(1, 10):
            if v(i, j, d) in sol:
                return d

    for i in range(1, 10):
        for j in range(1, 10):
            grid[i - 1][j - 1] = read_cell(i, j)


def is_proper(clauses):
    sol = pycosat.solve(clauses)
    clauses.append([-x for x in sol])
    sol = pycosat.solve(clauses)
    if isinstance(sol, list):
        return False
    return True


if __name__ == '__main__':
    from pprint import pprint

    # hard Sudoku problem, see Fig. 3 in paper by Weber
    """hard = [[0, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 6, 0, 0, 0, 0, 3],
            [0, 7, 4, 0, 8, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 0, 0, 2],
            [0, 8, 0, 0, 4, 0, 0, 1, 0],
            [6, 0, 0, 5, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 7, 8, 0],
            [5, 0, 0, 0, 0, 9, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 4, 0]]"""""

    first = numpy.array([[0, 2, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 6, 0, 0, 0, 0, 3],
                         [0, 0, 4, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 2],
                         [0, 8, 0, 0, 0, 0, 0, 1, 0],
                         [6, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0]])

    solve(first, 0)
    pprint(first)

    solve_time = numpy.zeros(82)
    solve_times = []

    """rows = []
    total_chance = 0
    for i in range(9):
        cols = numpy.where(hard[i] != 0)[0]
        if len(cols) != 0:
            total_chance += len(cols)
            rows.append(cols)
    print rows

    print total_chance
    for i in range(9):
        if len(cols) != 0:
            if random.randint(1,total_chance) == 1:

            total_chance -= len(cols)"""
    """hard = [[5, 3, 7, 4, 2, 1, 8, 9, 6],
            [6, 9, 4, 8, 3, 7, 2, 1, 5],
            [2, 1, 8, 9, 6, 5, 7, 4, 3],
            [1, 6, 9, 3, 8, 4, 5, 2, 7],
            [8, 2, 5, 1, 7, 9, 3, 6, 4],
            [7, 4, 3, 6, 5, 2, 1, 8, 9],
            [4, 8, 6, 7, 1, 3, 9, 5, 2],
            [9, 7, 2, 5, 4, 8, 6, 3, 1],
            [3, 5, 1, 2, 9, 6, 4, 7, 8]]"""

    for current_iteration in range(iteration_count):
        """ hard = [[5, 3, 7, 4, 2, 1, 8, 9, 6],
                 [6, 9, 4, 8, 3, 7, 2, 1, 5],
                 [2, 1, 8, 9, 6, 5, 7, 4, 3],
                 [1, 6, 9, 3, 8, 4, 5, 2, 7],
                 [8, 2, 5, 1, 7, 9, 3, 6, 4],
                 [7, 4, 3, 6, 5, 2, 1, 8, 9],
                 [4, 8, 6, 7, 1, 3, 9, 5, 2],
                 [9, 7, 2, 5, 4, 8, 6, 3, 1],
                 [3, 5, 1, 2, 9, 6, 4, 7, 8]]"""
        hard = numpy.copy(first)
        current_number = 0
        current = numpy.copy(hard)
        solve(current, current_number)
        i, j = numpy.nonzero(hard)
        # print i, j
        while len(i) != 0:
            current_number += 1
            rand = random.randint(0, len(i) - 1)
            hard[i[rand]][j[rand]] = 0
            # pprint(hard)

            current = numpy.copy(hard)
            solve(current, current_number)
            i, j = numpy.nonzero(hard)
            # print i, j

        print solve_time

deviations = numpy.zeros(82)
means = numpy.zeros(82)
for i in range(82):
    j = i
    current_deviations = []
    while j < len(solve_times):
        current_deviations.append(solve_times[j])
        j += 82
    deviations[i] = numpy.std(current_deviations)
    means[i] = numpy.mean(current_deviations)

numpy.savetxt('means.out', means, delimiter=',')  # X is an array
numpy.savetxt('deviations.out', deviations, delimiter=',')
numpy.savetxt('solve_times.out', solve_times, delimiter=',')
# print solve_time
plt.plot(means)
plt.show()
plt.plot(deviations)
plt.show()
