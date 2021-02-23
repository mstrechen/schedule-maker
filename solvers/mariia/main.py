from collections import namedtuple
from .genetic_algorithm import GeneticAlgorithm
from copy import deepcopy
import random

Gene = namedtuple('Gene', ['subject', 'group', 'teacher', 'classroom', 'pair'])
ScheduleEntry = namedtuple('ScheduleEntry', ['subject', 'class1', 'teacher1', 'class2', 'teacher2'])

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

    def is_valid(self, schedule):
        teacher_timeslot_pairs = set()
        classroom_timeslot_pairs = set()
        for group in range(self.groups_count):
            for timeslot in range(self.timeslots):
                entry = schedule[group][timeslot]
                if entry is None:
                    continue

                if (timeslot, entry.teacher1) in teacher_timeslot_pairs:
                    return False
                if (timeslot, entry.teacher2) in teacher_timeslot_pairs:
                    return False

                if (timeslot, entry.class1) in classroom_timeslot_pairs:
                    return False
                if (timeslot, entry.class2) in classroom_timeslot_pairs:
                    return False

                if self.is_lecture(entry.subject) and entry.class2 is not None:
                    return False

        return True

    def fitness(self, schedule):
        if not self.is_valid(schedule):
            return -1e9

        group_subject_count = [[0 for _ in range(self.subject_count)] for _ in range(self.groups_count)]
        for group in range(self.groups_count):
            for timeslot in range(self.timeslots):
                if schedule[group][timeslot] is not None:
                    group_subject_count[group][schedule[group][timeslot].subject] += 1

        score = 0
        for group in range(self.groups_count):
            for subject in range(self.subject_count):
                subject_score = min(self.study_plan_requirements[group][subject], group_subject_count[group][subject])
                score += 2 * subject_score

                # subject completion bonus
                if self.study_plan_requirements[group][subject] > 1 and self.study_plan_requirements[group][subject] == group_subject_count[group][subject]:
                    score += 1

        return score

    def crossover(self, parent1, parent2):
        most_fit_offspring = None
        max_fitness = -1e9

        for group in range(self.groups_count):
            timeslot = random.randint(0, self.timeslots - 1)
            offspring = deepcopy(parent1[0])

            for timeslots in range(timeslot + 1, self.timeslots):
                entry = offspring[group][timeslot]
                offspring[group][timeslot] = parent2[0][group][timeslot]
                if not self.is_valid(offspring):
                    offspring[group][timeslot] = entry

            fitness = self.fitness(offspring)
            if most_fit_offspring is None or fitness > max_fitness:
                most_fit_offspring = offspring
                max_fitness = fitness

        return most_fit_offspring

    def first_fit_group(self, group, schedule):
        start_subject = random.randint(0, self.subject_count)
        for offset in range(self.subject_count):
            subject = (start_subject + offset) % self.subject_count
            count = self.study_plan_requirements[group][subject]
            timeslots = [i for i in range(self.timeslots)]
            random.shuffle(timeslots)
            for timeslot in timeslots:
                if schedule[group][timeslot] is not None:
                    continue

                if self.is_lecture(subject):
                    for classroom in range(self.lecture_classroom_count):
                        for teacher in self.subject_to_teacher[subject]:
                            if count == 0:
                                break
                            schedule[group][timeslot] = ScheduleEntry(subject, teacher, classroom, None, None)
                            if self.is_valid(schedule):
                                count -= 1
                                continue
                            else:
                                schedule[group][timeslot] = None
                else:
                    for teacher1 in self.subject_to_teacher[subject]:
                        for teacher2 in self.subject_to_teacher[subject]:
                            if teacher2 == teacher1:
                                continue

                            for classroom1 in range(self.classroom_count):
                                for classroom2 in range(self.classroom_count):
                                    if classroom1 == classroom2:
                                        continue

                                    if count == 0:
                                        break

                                    schedule[group][timeslot] = ScheduleEntry(subject,
                                                                teacher1, classroom1, teacher2, classroom2)
                                    if self.is_valid(schedule):
                                        count -= 1
                                        continue
                                    else:
                                        schedule[group][timeslot] = None

        return schedule

    def gen_initial(self, n):
        population = []

        for individual in range(n):
            basic = [[None for _ in range(self.timeslots)] for _ in range(self.groups_count)]
            used = [False for _ in range(self.groups_count)]
            for _ in range(self.groups_count - 2):
                group_next = random.randint(0, self.groups_count-1)
                while used[group_next]:
                    group_next = random.randint(0, self.groups_count-1)
                basic = self.first_fit_group(group_next, basic)
                used[group_next] = True

            population.append(basic)

        return population

    def mutation(self, schedule):
        group = random.randint(0, self.groups_count - 1)
        candidates = []

        for timeslot in range(self.timeslots):
            candidate = deepcopy(schedule)
            if schedule[group][timeslot] is None:
                continue
            subject = schedule[group][timeslot].subject

            if self.is_lecture(subject):
                classroom = schedule[group][timeslot].class1
                teacher = random.choice(self.subject_to_teacher[subject])
                candidate[group][timeslot] = ScheduleEntry(subject, teacher, classroom, None, None)
            else:
                entry = candidate[group][timeslot]
                flip = random.random()
                if flip > 0.5:
                    teacher1, class1 = entry.teacher1, entry.class1
                    teacher2, class2 = entry.teacher2, entry.class2
                    entry = ScheduleEntry(subject, teacher2, class2, teacher1, class1)
                    candidate[group][timeslot] = entry

                change_teacher = random.random()
                if change_teacher > 0.5:
                    for _ in range(5):
                        teacher = random.choice(self.subject_to_teacher[subject])
                        candidate[group][timeslot] = ScheduleEntry(entry.subject, teacher,
                                                                   entry.class1, entry.teacher2, entry.class2)
                        if self.is_valid(candidate):
                            break
                else:
                    for _ in range(5):
                        classroom = random.randint(0, self.classroom_count - 1)
                        candidate[group][timeslot] = ScheduleEntry(entry.subject, entry.teacher1, classroom,
                                                                   entry.teacher2, entry.class2)
                        if self.is_valid(candidate):
                            break

            if self.is_valid(candidate):
                candidates.append(candidate)

        if len(candidates) == 0:
            return None

        return random.choice(candidates)

    @staticmethod
    def decode_timeslot(timeslot):
        return timeslot // CLASSES_PER_DAY, timeslot % CLASSES_PER_DAY

    def decode(self, schedule):
        count = 0
        for group in range(self.groups_count):
            for timeslot in range(self.timeslots):
                if schedule[group][timeslot] is None:
                    continue
                count += 1
                if schedule[group][timeslot].teacher2 is not None:
                    count += 1
        print(count)
        for group in range(self.groups_count):
            for timeslot in range(self.timeslots):
                if schedule[group][timeslot] is None:
                    continue
                entry = schedule[group][timeslot]
                day, pair = self.decode_timeslot(timeslot)
                print(entry.subject, entry.teacher1, group, entry.class1, day, pair)
                if entry.teacher2 is not None:
                    print(entry.subject, entry.teacher2, group, entry.class2, day, pair)

    def is_lecture(self, subject):
        return subject < self.lectures_count


if __name__ == '__main__':
    problem = ScheduleProblem()
    initial_population = problem.gen_initial(50)
    ga = GeneticAlgorithm(initial_population, problem.fitness, problem.crossover, problem.mutation, epochs=50)
    best_schedule = ga.fit()
    problem.decode(best_schedule)
