"""
Exercise 1 – Generalized Sudoku as a CSP

Requirements:
    pip install python-constraint

Run:
    python sudoku.py

Coordinates use (x, y):
    x = column (0–8)
    y = row (0–8)
"""

from contextlib import redirect_stdout
from itertools import product

from constraint import AllDifferentConstraint, Problem



# 1. Create the CSP and variables


problem = Problem()

# All 81 cell coordinates: (column, row).
board = list(product(range(9), range(9)))

# Every cell contains a number from 1 to 9.
for cell in board:
    problem.addVariable(cell, range(1, 10))



# 2. Standard Sudoku constraints


# Every 3x3 block contains different values.
for block_x in range(0, 9, 3):
    for block_y in range(0, 9, 3):
        block_cells = [
            (x, y)
            for x in range(block_x, block_x + 3)
            for y in range(block_y, block_y + 3)
        ]
        problem.addConstraint(
            AllDifferentConstraint(), block_cells
        )

# Every row contains different values.
for y in range(9):
    row_cells = [(x, y) for x in range(9)]
    problem.addConstraint(
        AllDifferentConstraint(), row_cells
    )

# Every column contains different values.
for x in range(9):
    column_cells = [(x, y) for y in range(9)]
    problem.addConstraint(
        AllDifferentConstraint(), column_cells
    )



# 3. Predefined cells from the puzzle


fixed_cells = {
    (4, 1): 2,
    (4, 2): 7,
    (1, 4): 1,
    (2, 4): 6,
    (6, 4): 8,
    (7, 4): 3,
    (4, 6): 5,
    (4, 7): 4,
}

for cell, given_value in fixed_cells.items():
    problem.addConstraint(
        lambda value, expected=given_value: value == expected,
        [cell],
    )



# 4. Additional constraint 2:
#    The four corners of the entire board sum to 10.


problem.addConstraint(
    lambda a, b, c, d: a + b + c + d == 10,
    [(0, 0), (0, 8), (8, 0), (8, 8)],
)



# 5. Additional constraint 3:
#    Bottom-left 3x3 block:
#    its four corners sum to twice its center.


problem.addConstraint(
    lambda top_left, top_right, bottom_left,
           bottom_right, center:
        top_left + top_right + bottom_left + bottom_right
        == 2 * center,
    [(0, 6), (2, 6), (0, 8), (2, 8), (1, 7)],
)



# 6. Additional constraint 4:
#    Arithmetic clues in the upper-left 3x3 block.


# The two top-left cells add up to 11.
problem.addConstraint(
    lambda a, b: a + b == 11,
    [(0, 0), (1, 0)],
)

# The specified difference is 6.
problem.addConstraint(
    lambda a, b: a - b == 6,
    [(2, 0), (2, 1)],
)

# Division clue: numerator / denominator = 2.
# Exact integer encoding avoids floating-point arithmetic.
problem.addConstraint(
    lambda numerator, denominator:
        numerator == 2 * denominator,
    [(0, 1), (1, 1)],
)

# The product of the three cells is 90.
problem.addConstraint(
    lambda a, b, c: a * b * c == 90,
    [(0, 2), (1, 2), (2, 2)],
)



# 7. Additional constraint 5:
#    Three columns in the bottom-right block increase
#    strictly from top to bottom.


for x in (6, 7, 8):
    problem.addConstraint(
        lambda top, middle, bottom:
            top < middle < bottom,
        [(x, 6), (x, 7), (x, 8)],
    )



# 8. Additional constraint 6:
#    Upper-right block adjacency.
#
#    Each corner must have at least one of its two
#    adjacent cells within the block equal to corner + 1.


def has_successor(corner, adjacent1, adjacent2):
    return (
        adjacent1 == corner + 1
        or adjacent2 == corner + 1
    )


# Upper-left corner.
problem.addConstraint(
    has_successor,
    [(6, 0), (7, 0), (6, 1)],
)

# Upper-right corner.
problem.addConstraint(
    has_successor,
    [(8, 0), (7, 0), (8, 1)],
)

# Lower-left corner.
problem.addConstraint(
    has_successor,
    [(6, 2), (7, 2), (6, 1)],
)

# Lower-right corner.
problem.addConstraint(
    has_successor,
    [(8, 2), (7, 2), (8, 1)],
)



# 9. Additional constraint 7:
#    A and all four B cells have opposite parity.


A_cell = (4, 4)

B_cells = [
    (4, 3),
    (3, 4),
    (5, 4),
    (4, 5),
]

for B_cell in B_cells:
    problem.addConstraint(
        lambda a, b: a % 2 != b % 2,
        [A_cell, B_cell],
    )


# 10. Solve the CSP


solutions = problem.getSolutions()

print(f"Number of solutions: {len(solutions)}")

if not solutions:
    raise RuntimeError(
        "The CSP solver did not find a solution."
    )



# 11. Print one solution


def print_solution(solution):

    board_str = ""

    for y in range(9):

        if y % 3 == 0 and y > 0:
            board_str += "---------------------\n"

        for x in range(9):

            if x % 3 == 0 and x > 0:
                board_str += "| "

            board_str += f"{solution[(x, y)]} "

        board_str += "\n"

    print(board_str)



# 12. Verify a solution against all constraints


def verify_solution(solution):

    # Every cell contains a number from 1 to 9.
    assert all(
        1 <= solution[cell] <= 9
        for cell in board
    )

    # Predefined cells.
    assert all(
        solution[cell] == value
        for cell, value in fixed_cells.items()
    )

    # Every row contains numbers 1 to 9 exactly once.
    for y in range(9):
        assert {
            solution[(x, y)] for x in range(9)
        } == set(range(1, 10))

    # Every column contains numbers 1 to 9 exactly once.
    for x in range(9):
        assert {
            solution[(x, y)] for y in range(9)
        } == set(range(1, 10))

    # Every 3x3 block contains numbers 1 to 9 exactly once.
    for block_x in range(0, 9, 3):
        for block_y in range(0, 9, 3):
            assert {
                solution[(x, y)]
                for x in range(block_x, block_x + 3)
                for y in range(block_y, block_y + 3)
            } == set(range(1, 10))

    # Constraint 2: board corners sum to 10.
    assert (
        solution[(0, 0)]
        + solution[(0, 8)]
        + solution[(8, 0)]
        + solution[(8, 8)]
        == 10
    )

    # Constraint 3: bottom-left block.
    assert (
        solution[(0, 6)]
        + solution[(2, 6)]
        + solution[(0, 8)]
        + solution[(2, 8)]
        == 2 * solution[(1, 7)]
    )

    # Constraint 4: upper-left arithmetic clues.
    assert solution[(0, 0)] + solution[(1, 0)] == 11

    assert solution[(2, 0)] - solution[(2, 1)] == 6

    assert solution[(0, 1)] == 2 * solution[(1, 1)]

    assert (
        solution[(0, 2)]
        * solution[(1, 2)]
        * solution[(2, 2)]
        == 90
    )

    # Constraint 5: bottom-right increasing sequences.
    for x in (6, 7, 8):
        assert (
            solution[(x, 6)]
            < solution[(x, 7)]
            < solution[(x, 8)]
        )

    # Constraint 6: upper-right block adjacency.
    assert (
        solution[(7, 0)] == solution[(6, 0)] + 1
        or solution[(6, 1)] == solution[(6, 0)] + 1
    )

    assert (
        solution[(7, 0)] == solution[(8, 0)] + 1
        or solution[(8, 1)] == solution[(8, 0)] + 1
    )

    assert (
        solution[(7, 2)] == solution[(6, 2)] + 1
        or solution[(6, 1)] == solution[(6, 2)] + 1
    )

    assert (
        solution[(7, 2)] == solution[(8, 2)] + 1
        or solution[(8, 1)] == solution[(8, 2)] + 1
    )

    # Constraint 7: A and all B cells have opposite parity.
    assert all(
        solution[A_cell] % 2 != solution[cell] % 2
        for cell in B_cells
    )

    return True


# Verify every solution returned by the CSP solver.
for solution in solutions:
    verify_solution(solution)

print(
    f"Verified all {len(solutions)} solutions "
    "against every constraint."
)



# 13. Display the first solution


print_solution(solutions[0])



# 14. Write actual solver output to sudoku.log


with open("sudoku.log", "w", encoding="utf-8") as logfile:

    with redirect_stdout(logfile):

        print(f"Number of solutions: {len(solutions)}")
        print()

        print_solution(solutions[0])

        print(
            f"Verified all {len(solutions)} solutions "
            "against every constraint."
        )

print("Saved the solver output to sudoku.log.")
