import typing as t
from collections import namedtuple

from solvers.mapper import get_mapper

from subprocess import Popen, PIPE, STDOUT


ScheduleEntity = namedtuple('ScheduleEntity', ['subject', 'teacher', 'group', 'classroom', 'day', 'pair'])


def run_mariia(input_data: str) -> str:
    p = Popen(['python3', 'solvers/mariia/main.py'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data, *_ = p.communicate(input=input_data.encode())
    if stderr_data:
        raise ValueError(stderr_data)
    return stdout_data.decode()


def run_stasian(param: str):
    def inner(input_data: str) -> str:
        o = open('solvers/stasian/input.txt', 'w')
        o.write(input_data)
        o.close()
        p = Popen(['./main.out', param], stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./solvers/stasian')
        p.communicate()
        p.kill()
        o = open('solvers/stasian/output.txt', 'r')
        return o.read()
    return inner


def get_full_schedule(solver) -> t.List[ScheduleEntity]:
    mapper = get_mapper()
    input_data = render_input_data(
        groups=mapper.groups,
        teachers=mapper.teachers,
        subjects=mapper.subjects,
        number_of_subjects_which_are_lectures=mapper.number_of_lectures,
        classrooms=mapper.classrooms,
        number_of_classrooms_which_are_for_lectures=mapper.number_of_big_classrooms,
        teacher_to_subject=mapper.translate_teacher_to_subject(mapper.teacher_to_subject),
        group_to_subject=mapper.translate_group_to_subject(mapper.group_to_subject),
    )
    output = RUNNERS[solver](input_data=input_data)
    raw_schedule = mapper.parse_schedule(output)
    return [
        ScheduleEntity(*entity) for entity in mapper.translate_schedule(raw_schedule)
    ]

def render_input_data(
        groups,
        teachers,
        subjects,
        number_of_subjects_which_are_lectures,
        classrooms,
        number_of_classrooms_which_are_for_lectures,
        teacher_to_subject,
        group_to_subject
):
    teacher_to_subject_rendered = '\n'.join(
        f'{tts[1]} {tts[0]}'
        for tts in teacher_to_subject
    )
    group_to_subject_rendered = '\n'.join(
        f'{gts[1]} {gts[0]} {gts[2]}'
        for gts in group_to_subject
    )
    return \
f"""{len(groups)}
{len(teachers)}
{len(subjects)} {number_of_subjects_which_are_lectures}
{len(classrooms)} {number_of_classrooms_which_are_for_lectures}
{len(teacher_to_subject)}
{teacher_to_subject_rendered}
{len(group_to_subject)}
{group_to_subject_rendered}
    """


RUNNERS = {
    'mariia': run_mariia,
    'stasian': run_stasian('0'),
    'stasian_1': run_stasian('1'),
}