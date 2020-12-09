# Loopy

## Inspiration

The Loopy puzzle on the Genius Puzzles app on iOS is a very fun and challenging time sink which stretches your deductive reasoning.
I recommend checking it out before using this solver. The basic idea of this puzzle is to mark one loop that goes by each numbered constraint exactly the specified number of times.

I was stuck on one of the square grid levels and thought about the strategies I was using to solve it, and realized that they can be generalized to an optimization problem. I converted the puzzle into a set of constraints and was pleasantly surprised that it solves the puzzle!

## A bit about the implementation details

The puzzle can be represented as a set of vertices and connecting edges that form the grid.

Each edge can either be marked (part of the loop) or unmarked, and are our decision variables.

The three constraints are:
1. Cycle constraint: for each vertex, the number of marked, connecting edges is either 0 or 2
2. Box constraint: each grid box, represented by 4 edges, must have an exact number of edges marked if specified
3. One cycle: the marked edges must form a single cycle.

I was not able to linearize the third constraint, so instead, I pruned solutions if the number of cycles in the resulting output is greater than 1.

## Usage

```
$ ./loopy_solver.py <filename>
```

Input file should be formatted as the example below:
```
7
7
___3_01
1_3____
2____2_
3_01113
__01___
_3__2__
_2322_3
```

The first two lines represent the number of rows and columns of the grid.
The rest of the file should match the loopy puzzle, with `_` denoting an empty square.

