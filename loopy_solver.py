#!/usr/local/bin/python3
from collections import defaultdict
from operator import add
import sys

from pulp import *
from union_find import *


def solve():
    ROWS, COLS, constraints = parse()

    VERTICES, EDGES, VERT_TO_EDGES = structures(ROWS, COLS)

    print("input grid:")
    output_grid(ROWS, COLS, constraints, EDGES)

    loopy = LpProblem("Loopy")

    # Decision variables: if edge is chosen for path
    choices = LpVariable.dicts("Choice", EDGES, cat="Binary")

    # Cycle constraints
    for vert in VERTICES:
        edges = VERT_TO_EDGES[vert]
        s = lpSum([choices[edge] for edge in edges])  # count of chosen edges for a vertex
        z1 = LpVariable(str(vert)+"1", lowBound=0, cat="Integer")  # positive component
        z2 = LpVariable(str(vert)+"2", lowBound=0, cat="Integer")  # negative component
        loopy += s - 1 == z1 - z2  # represent absolute value of count - 1
        loopy += z1 + z2 == 1  # count is either 0 or 2

    # Box number constraints
    for (i, j), v in constraints.items():
        edges = vert_to_box_edges(i, j)

        s = lpSum([choices[edge] for edge in edges])  # count of chosen edges for a vertex
        loopy += s == v

    # Solve
    loopy.solve(PULP_CBC_CMD(msg=0))
    status = LpStatus[loopy.status]
    print("status:", status)

    if status != "Optimal":
        return

    iteration = 1
    number_of_cycles = cycle_count(VERTICES, choices)
    print("iteration", iteration, "number of cycles", number_of_cycles)

    # Prune solutions until contains only once cycle
    while number_of_cycles != 1:
        # ensure same solution cannot be reached
        _, path = pos_choices(choices)
        loopy += lpSum(path) <= len(path) - 1

        loopy.solve(PULP_CBC_CMD(msg=0))
        number_of_cycles = cycle_count(VERTICES, choices)

        iteration += 1
        print("iteration", iteration, "number of cycles", number_of_cycles)

    print("solution grid:")
    edges, _ = pos_choices(choices)
    output_grid(ROWS, COLS, constraints, edges)


def parse():
    if len(sys.argv) != 2:
        print("Usage: loopy_solver.py <filename>")
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


def pos_choices(choices):
    return zip(*filter(lambda choice: value(choice[1]) == 1, choices.items()))


def cycle_count(vertices, choices):
    graph = Graph(vertices)

    graph_edges, _ = pos_choices(choices)
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
