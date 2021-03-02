from copy import deepcopy
try:
    from solvers.csp.heuristics import is_compatible
except:
    try:
        from .heuristics import is_compatible
    except:
        from heuristics import is_compatible

from itertools import combinations


# Dummy implementation for next variable selection - returns first non-used variable
def first_not_used(domain, used, assignments, is_valid):
    for variable in range(len(domain)):
        if variable not in used:
            return variable


# Dummy implementation for possible values of a variable - ordering - uses default order
def no_transform(variable, domains, used, assignments, is_valid):
    return domains[variable]


class CSP:
    def __init__(self, variables, domains, is_valid, select_variable=first_not_used, order_values=no_transform,
                 forward_checking=False, constraint_propagation=False):
        self.variables = variables
        self.domains = domains
        self.is_valid = is_valid
        self.select_variable = select_variable
        self.order_values = order_values
        self.forward_checking = forward_checking
        self.constraint_propagation = constraint_propagation

    # process_assignment function do corresponding checks for forward_checking and maintaining arc consistency.
    # It returns applied restrictions(for future rollback) and flag for branch failure detected
    def process_assignment(self, value, used):
        if not self.forward_checking and not self.constraint_propagation:
            return [], False

        # Forward checking
        deleted_entries = []
        for other_variable in range(len(self.variables)):
            if other_variable in used:
                continue

            other_values_to_delete = []
            for other_value in self.domains[other_variable]:
                if not is_compatible(value, other_value):
                    deleted_entries.append((other_variable, other_value))
                    other_values_to_delete.append(other_value)

            for other_value in other_values_to_delete:
                self.domains[other_variable].remove(other_value)

            # forward-checking: if domain is empty for some unfulfilled variable -> branch failure
            if len(self.domains[other_variable]) == 0:
                return deleted_entries, True

        if not self.constraint_propagation:
            return deleted_entries, False

        # Constraint propagation
        deleted_on_level = deepcopy(deleted_entries)
        while len(deleted_on_level) != 0:
            deleted_on_level.clear()
            for variable, other_variable in combinations(range(len(self.variables)), 2):
                if variable in used or other_variable in used:
                    continue
                for value in self.domains[variable]:
                    exists_compatible = False
                    for other_value in self.domains[other_variable]:
                        if is_compatible(value, other_value):
                            exists_compatible = True
                            break
                    if not exists_compatible:
                        deleted_on_level.append((variable, value))

            for entry in deleted_on_level:
                self.domains[entry[0]].remove(entry[1])

            deleted_entries.extend(deleted_on_level)

        return deleted_entries, False

    def rollback_assignment(self, arcs_to_restore):
        for entry in arcs_to_restore:
            variable = entry[0]
            value = entry[1]
            self.domains[variable].add(value)

    def gen(self, n, used, assignments):
        if len(used) == n:
            return assignments
        next_var = self.select_variable(self.domains, used, assignments, self.is_valid)
        used.add(next_var)
        values = self.order_values(next_var, self.domains, used, assignments, self.is_valid)
        for next_value in values:
            assignments.append((next_var, next_value))
            if self.is_valid(assignments):
                arcs_to_restore = self.process_assignment(next_value, used)
                solution = self.gen(n, used, assignments)
                if solution is not None:
                    return solution
                self.rollback_assignment(arcs_to_restore)
            assignments.remove((next_var, next_value))
        used.remove(next_var)

    def solve(self):
        return self.gen(len(self.variables), set(), [])
