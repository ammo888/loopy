#!/usr/local/bin/python3
from collections import defaultdict
from operator import add
import sys

from ortools.sat.python import cp_model
from union_find import *


def solve():
    ROWS, COLS, constraints = parse()
    print("constraints:", constraints)

    VERTICES, EDGES, VERT_TO_EDGES = structures(ROWS, COLS)

    loopy = cp_model.CpModel()
    solver = cp_model.CpSolver()

    # Decision variables: if edge is chosen for path
    choices = {edge: loopy.NewBoolVar("Choice[{0}]".format(edge)) for edge in EDGES}

    # Cycle constraints
    for vert in VERTICES:
        edges = VERT_TO_EDGES[vert]
        s = sum(choices[edge] for edge in edges)
        z1 = loopy.NewIntVar(0, 4, "z1[{0}]".format(vert))  # positive component
        z2 = loopy.NewIntVar(0, 4, "z2[{0}]".format(vert))  # negative component
        loopy.Add(s - 1 == z1 - z2)  # represent absolute value of count - 1
        loopy.Add(z1 + z2 == 1)  # count is either 0 or 2

    # Box number constraints
    print("box constraints:")
    for (i, j), v in constraints.items():
        edges = vert_to_box_edges(i, j)
        print("vertex:", (i, j), "value:", v, "edges:", edges)

        s = sum(choices[edge] for edge in edges)  # count of chosen edges for a vertex

        loopy.Add(s == v)

    # Solve
    status = solver.Solve(loopy)
    if status != cp_model.OPTIMAL:
        print("status: infeasible")
        return

    print("status: optimal")
    iteration = 1
    number_of_cycles = cycle_count(solver, VERTICES, choices)
    print("iteration", iteration, "number of cycles", number_of_cycles)

    # Prune solutions until contains only once cycle
    while number_of_cycles != 1:
        # ensure same solution cannot be reached
        _, path = pos_choices(solver, choices)
        loopy.Add(sum(path) != len(path))

        status = solver.Solve(loopy)
        number_of_cycles = cycle_count(solver, VERTICES, choices)

        iteration += 1
        print("iteration", iteration, "number of cycles", number_of_cycles)

    print("input grid:")
    output_grid(ROWS, COLS, constraints, EDGES)

    print("solution grid:")
    edges, _ = pos_choices(solver, choices)
    output_grid(ROWS, COLS, constraints, edges)


def parse():
    if len(sys.argv) != 2:
        print("Usage: loopy_solver_ortools.py <filename>")
        exit(1)

    filename = sys.argv[1]
    with open(filename, 'r') as fp:
        rows = int(fp.readline().strip())
        cols = int(fp.readline().strip())

        constraints = dict()
        for i in range(rows):
            for j in range(cols):
                c = fp.read(1)
                if c != '_':
                    constraints[(i, j)] = int(c)
            fp.readline()

        return (rows, cols, constraints)


def structures(rows, cols):
    vertices = [(i, j) for i in range(rows+1) for j in range(cols+1)]
    edges = list()  # edges are in lexicographic order
    vert_to_edges = defaultdict(list)

    for (i, j) in vertices:
        vert = (i, j)
        vert1 = (i+1, j)
        vert2 = (i, j+1)
        edge1 = (vert, vert1)
        edge2 = (vert, vert2)
        if i < rows:
            edges.append(edge1)
            vert_to_edges[vert].append(edge1)
            vert_to_edges[vert1].append(edge1)
        if j < cols:
            edges.append(edge2)
            vert_to_edges[vert].append(edge2)
            vert_to_edges[vert2].append(edge2)

    return vertices, edges, vert_to_edges


def vert_to_box_edges(i, j):
    return [((i, j), (i+1, j)),
            ((i, j), (i, j+1)),
            ((i+1, j), (i+1, j+1)),
            ((i, j+1), (i+1, j+1))]


def pos_choices(solver, choices):
    return zip(*filter(lambda choice: solver.BooleanValue(choice[1]), choices.items()))


def cycle_count(solver, vertices, choices):
    graph = Graph(vertices)

    graph_edges, _ = pos_choices(solver, choices)
    for vert1, vert2 in graph_edges:
        graph.add_edge(vert1, vert2)

    return num_cycles(graph)


def output_grid(rows, cols, constraints, edges):
    # Character grid
    grid = [[" " for j in range(cols+cols+1)] for i in range(rows+rows+1)]

    # Add box constraints
    for (i, j), v in constraints.items():
        grid[2*i+1][2*j+1] = str(v)

    # Add edge choices
    for (vert1, vert2) in edges:
        (i, j) = map(add, vert1, vert2)
        if (vert1[0] < vert2[0]):
            c = "|"
        else:
            c = "-"
        grid[i][j] = c

    # Print solution
    for row in grid:
        print(''.join(row))


if __name__ == "__main__":
    solve()
