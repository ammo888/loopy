from collections import defaultdict


class Graph:

    def __init__(self, vertices):
        self.vertices = vertices
        self.edges = defaultdict(list)

    def add_edge(self, u, v):
        self.edges[u].append(v)


class Subset:
    def __init__(self, parent, rank):
        self.parent = parent
        self.rank = rank


def find(subsets, node):
    if subsets[node].parent != node:
        subsets[node].parent = find(subsets, subsets[node].parent)
    return subsets[node].parent


def union(subsets, u, v):
    if subsets[u].rank > subsets[v].rank:
        subsets[v].parent = u
    elif subsets[v].rank > subsets[u].rank:
        subsets[u].parent = v
    else:
        subsets[v].parent = u
        subsets[u].rank += 1


def num_cycles(graph):
    subsets = dict()

    for u in graph.vertices:
        subsets[u] = Subset(u, 0)

    cycle_count = 0

    for u in graph.edges:
        u_rep = find(subsets, u)

        for v in graph.edges[u]:
            v_rep = find(subsets, v)

            if u_rep == v_rep:
                cycle_count += 1
            else:
                union(subsets, u_rep, v_rep)

    return cycle_count
