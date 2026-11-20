
from constraint import Problem
from itertools import combinations
from contextlib import redirect_stdout



# 1. Input data


teams = ["A", "B", "C", "D"]

location_available = {
    "A": [1, 4, 6, 7, 8, 10],
    "B": [2, 4, 5, 6, 7, 9],
    "C": [2, 3, 5, 8, 10],
    "D": [1, 3, 6, 8, 9, 10],
}



# 2. Create the CSP


problem = Problem()

# One variable for every unordered pair of teams.
team_pairs = list(combinations(teams, 2))

variables = []

for team1, team2 in team_pairs:

    variable = f"match_{team1}_{team2}"
    variables.append(variable)

    domain = []

    # Either team can host the first-half match.
    for first_home, second_home in (
        (team1, team2),
        (team2, team1)
    ):

        # The first match takes place at first_home.
        for first_slot in location_available[first_home]:

            # The return match takes place at second_home.
            for second_slot in location_available[second_home]:

                # The return match must occur after the first match.
                if first_slot < second_slot:
                    domain.append(
                        (first_home, first_slot, second_slot)
                    )

    problem.addVariable(variable, domain)



# 3. Helper function: expand a pair into two matches


def expand_pair(pair, value):

    team1, team2 = pair

    first_home, first_slot, second_slot = value

    # Determine the away team in the first match.
    first_away = team2 if first_home == team1 else team1

    # First-half match and return match.
    return [
        (first_home, first_away, first_slot),
        (first_away, first_home, second_slot)
    ]



# 4. Constraint 2:
#    A team can play at most once per time slot.


def teams_do_not_overlap(pair1, value1, pair2, value2):

    matches1 = expand_pair(pair1, value1)
    matches2 = expand_pair(pair2, value2)

    for home1, away1, slot1 in matches1:

        for home2, away2, slot2 in matches2:

            if slot1 == slot2:

                teams1 = {home1, away1}
                teams2 = {home2, away2}

                # The matches must not share a team.
                if teams1.intersection(teams2):
                    return False

    return True



# 5. Constraint 3:
#    A location can host at most one match per slot.


def locations_do_not_overlap(pair1, value1, pair2, value2):

    matches1 = expand_pair(pair1, value1)
    matches2 = expand_pair(pair2, value2)

    for home1, away1, slot1 in matches1:

        for home2, away2, slot2 in matches2:

            if home1 == home2 and slot1 == slot2:
                return False

    return True


# Add constraints 2 and 3 between all different pairs.
for pair1, pair2 in combinations(team_pairs, 2):

    variable1 = f"match_{pair1[0]}_{pair1[1]}"
    variable2 = f"match_{pair2[0]}_{pair2[1]}"

    problem.addConstraint(
        lambda v1, v2, p1=pair1, p2=pair2:
            teams_do_not_overlap(p1, v1, p2, v2),
        [variable1, variable2]
    )

    problem.addConstraint(
        lambda v1, v2, p1=pair1, p2=pair2:
            locations_do_not_overlap(p1, v1, p2, v2),
        [variable1, variable2]
    )



# 6. Constraint 5:
#    All first-half matches must finish before
#    any second-half match begins.


def first_half_finishes_before_second_half(*assignments):

    first_half_slots = [value[1] for value in assignments]
    second_half_slots = [value[2] for value in assignments]

    return max(first_half_slots) < min(second_half_slots)


problem.addConstraint(
    first_half_finishes_before_second_half,
    variables
)



# 7. Constraint 6:
#    Preserve the ordering of return matches.


def preserve_return_match_order(value1, value2):

    first_slot1 = value1[1]
    second_slot1 = value1[2]

    first_slot2 = value2[1]
    second_slot2 = value2[2]

    # If match 1 is earlier in the first half,
    # its return match must also be earlier.
    if first_slot1 < first_slot2:
        return second_slot1 < second_slot2

    # If match 2 is earlier in the first half,
    # its return match must also be earlier.
    elif first_slot1 > first_slot2:
        return second_slot1 > second_slot2

    # If both first-half matches occur simultaneously,
    # there is no relative ordering to preserve.
    else:
        return True


# Apply constraint 6 to every pair of variables.
for pair1, pair2 in combinations(team_pairs, 2):

    variable1 = f"match_{pair1[0]}_{pair1[1]}"
    variable2 = f"match_{pair2[0]}_{pair2[1]}"

    problem.addConstraint(
        preserve_return_match_order,
        [variable1, variable2]
    )



# 8. Find all solutions


solutions = problem.getSolutions()

print(f"Number of solutions: {len(solutions)}")

if not solutions:
    raise RuntimeError("No valid schedule was found.")



# 9. Print a solution


def print_solution(solution):

    matches = []

    for pair in team_pairs:

        variable = f"match_{pair[0]}_{pair[1]}"

        matches.extend(
            expand_pair(pair, solution[variable])
        )

    # Sort matches by time slot, then home and away team.
    matches.sort(key=lambda match: (match[2], match[0], match[1]))

    for home, away, slot in matches:

        print(f"{home} vs {away} at {home} in slot {slot}")


# Print the first solution.
print_solution(solutions[0])



# 10. Write the results to scheduling.log


with open("scheduling.log", "w", encoding="utf-8") as logfile:

    with redirect_stdout(logfile):

        print(f"Number of solutions: {len(solutions)}")
        print()

        print_solution(solutions[0])


print("Results written to scheduling.log")
