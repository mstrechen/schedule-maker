from collections import namedtuple

try:
    from solvers.csp.csp import CSP, no_transform, first_not_used
    from solvers.csp.heuristics import lcv, MCV, mrv
except:
    try:
        from .csp import CSP, no_transform, first_not_used
        from .heuristics import lcv, MCV, mrv
    except:
        from csp import CSP, no_transform, first_not_used
        from heuristics import lcv, MCV, mrv

import sys

ScheduleEntry = namedtuple('ScheduleEntry', ['timeslot', 'classroom', 'teacher'])

# Each variable decodes class from study plan requirement
Variable = namedtuple('Variable', ['group', 'subject'])

DAY_PER_WEEK = 5
CLASSES_PER_DAY = 4


class ScheduleProblem:
    def __init__(self):
        self.groups_count = int(input())
        self.teachers_count = int(input())
        self.timeslots = DAY_PER_WEEK * CLASSES_PER_DAY
        self.subject_count, self.lectures_count = map(int, input().split())
        self.classroom_count, self.lecture_classroom_count = map(int, input().split())
        self.subject_teacher_pairs = int(input())
        self.subject_to_teacher = [[] for _ in range(self.subject_count)]
        for i in range(self.subject_teacher_pairs):
            subject, teacher = map(int, input().split())
            self.subject_to_teacher[subject].append(teacher)

        self.study_plan_requirements_count = int(input())
        self.study_plan_requirements = [[0 for _ in range(self.subject_count)] for _ in range(self.groups_count)]
        for i in range(self.study_plan_requirements_count):
            subject, group, count = map(int, input().split())
            self.study_plan_requirements[group][subject] = count
        self.variables = self.get_variables()

    @staticmethod
    def is_valid(assignments):
        teacher_timeslot_pairs = set()
        classroom_timeslot_pairs = set()

        for assignment in assignments:
            entry = assignment[1]
            if entry is None:
                continue

            teacher_timeslot_pair = (entry.timeslot, entry.teacher)
            if teacher_timeslot_pair in teacher_timeslot_pairs:
                return False
            teacher_timeslot_pairs.add(teacher_timeslot_pair)

            classroom_timeslot_pair = (entry.timeslot, entry.classroom)
            if classroom_timeslot_pair in classroom_timeslot_pairs:
                return False
            classroom_timeslot_pairs.add(classroom_timeslot_pair)

        return True

    def get_variables(self):
        variables = []
        for group in range(self.groups_count):
            for subject in range(self.subject_count):
                for lesson in range(self.study_plan_requirements[group][subject]):
                    variables.append(Variable(group, subject))
        return variables

    def get_domains(self):
        domains = []

        for variable in range(len(self.variables)):
            decoded_variable = self.variables[variable]
            variable_domain = set()

            # Listing all the valid schedule entries for each variable
            for teacher in self.subject_to_teacher[decoded_variable.subject]:
                classrooms_count = self.lecture_classroom_count if self.is_lecture(decoded_variable.subject) \
                    else self.classroom_count
                for classroom in range(classrooms_count):
                    for timeslot in range(self.timeslots):
                        variable_domain.add(ScheduleEntry(timeslot, classroom, teacher))

            domains.append(variable_domain)

        return domains

    @staticmethod
    def decode_timeslot(timeslot):
        return timeslot // CLASSES_PER_DAY, timeslot % CLASSES_PER_DAY

    def decode(self, assignments):
        print(len(assignments))

        for assignment in assignments:
            variable = assignment[0]
            decoded_variable = self.variables[variable]
            entry = assignment[1]
            day, pair = self.decode_timeslot(entry.timeslot)
            print(decoded_variable.subject, entry.teacher, decoded_variable.group, entry.classroom, day, pair)

    def is_lecture(self, subject):
        return subject < self.lectures_count


if __name__ == '__main__':
    problem = ScheduleProblem()

    select_variable_val = None
    if sys.argv[1] == "first_not_used":
        select_variable_val = first_not_used
    elif sys.argv[1] == "mrv":
        select_variable_val = mrv
    else:
        select_variable_val = MCV(problem.variables, problem.subject_to_teacher).mcv

    if sys.argv[2] == "no_transform":
        order_values_val = no_transform
    else:
        order_values_val = lcv


    csp = CSP(problem.variables, problem.get_domains(), problem.is_valid,
              select_variable=MCV(problem.variables, problem.subject_to_teacher).mcv,
              order_values=lcv, forward_checking=(sys.argv[3] == "true"), constraint_propagation=(sys.argv[4] == "true"))
    solution = csp.solve()
    problem.decode(solution)
