# MRV(Minimum Remaining Values) is a heuristic to choose next variable for assignment
# Algorithm chooses variable that has smallest domain of allowed values left
def mrv(domains, used, assignments, is_valid):
    mrv_value = 1e9
    mrv_variable = None

    for variable in range(len(domains)):
        if variable in used:
            continue

        remaining_values = 0
        for value in domains[variable]:
            if is_valid(assignments + [(variable, value)]):
                remaining_values += 1

        if remaining_values < mrv_value:
            mrv_value = remaining_values
            mrv_variable = variable

    return mrv_variable


# MCV(Most Constraining Variable or degree heuristic) is a heuristic to choose next variable for assignment
# Algorithm chooses variable that put most restrictions on unassigned variables
class MCV:
    def __init__(self, variables, subject_to_teacher):
        self.variables = variables
        self.subject_to_teacher = subject_to_teacher

    # Degree for the heuristic is calculated based on how many variables for the same group are not assigned
    # and how many other variables may be in need of a current variable subject
    def mcv(self, domains, used, assignments, is_valid):
        max_degree = 0
        max_degree_variable = None
        for variable_index, variable in enumerate(self.variables):
            if variable_index in used:
                continue

            degree = 0
            for other_variable in self.variables:
                if other_variable in used or other_variable == variable:
                    continue

                if variable.group == other_variable.group:
                    degree += 1

                if variable.subject == other_variable.subject:
                    degree += 1

            if degree > max_degree:
                max_degree = degree
                max_degree_variable = variable_index

        return max_degree_variable


# LCV(Least Constraining Value) is a heuristic to order values for assignment to current variable
# Algorithm chooses value, assigment to which, removes least possible amount of options for unassigned variables
def lcv(variable, domains, used, assignments, is_valid):
    scores = []
    for value in domains[variable]:
        if not is_valid(assignments + [(variable, value)]):
            continue

        score = 0
        for other_variable in range(len(domains)):
            if variable == other_variable or other_variable in used:
                continue

            for other_value in domains[other_variable]:
                if not is_compatible(value, other_value):
                    score += 1
        scores.append((score, value))

    sorted_scores = sorted(scores)
    sorted_domain = [entry[1] for entry in sorted_scores]

    return sorted_domain


# helper function to determine if two schedule entries are compatible
def is_compatible(entry1, entry2):
    if entry1.timeslot == entry2.timeslot:
        if entry1.teacher == entry2.teacher:
            return False
        if entry1.classroom == entry2.classroom:
            return False
    return True
