import typing as t
from collections import namedtuple

from db import db

Group = namedtuple('Group', ['group_name'])
Teacher = namedtuple('Teacher', ['name'])
Subject = namedtuple('Subject', ['subject_name', 'is_lecture'])
Classroom = namedtuple('Classroom', ['classroom_name', 'is_for_lecture'])
TeacherToSubject = namedtuple('TeacherToSubject', ['name', 'subject_name'])
GroupToSubject = namedtuple('GroupToSubject', ['group_name', 'subject_name', 'number_of_hours'])


class AlmostOrm:
    @property
    def groups(self) -> t.List[Group]:
        return list(map(
            lambda res: Group(**res),
            db.execute('SELECT group_name FROM groups ORDER BY group_name')
        ))

    @property
    def teachers(self) -> t.List[Teacher]:
        return list(map(
            lambda res: Teacher(**res),
            db.execute('SELECT name FROM teachers ORDER BY name')
        ))

    @property
    def classrooms(self) -> t.List[Classroom]:
        return list(map(
            lambda res: Classroom(**res),
            db.execute('SELECT classroom_name, is_for_lecture FROM classrooms ORDER BY is_for_lecture DESC , classroom_name')
        ))

    @property
    def subjects(self) -> t.List[Subject]:
        return list(map(
            lambda res: Subject(**res),
            db.execute('SELECT subject_name, is_lecture FROM subjects ORDER BY is_lecture DESC , subject_name')
        ))

    @property
    def teacher_to_subject(self) -> t.List[TeacherToSubject]:
        return list(map(
            lambda res: TeacherToSubject(**res),
            db.execute('SELECT name, subject_name FROM teacher_to_subject')
        ))

    @property
    def group_to_subject(self) -> t.List[GroupToSubject]:
        return list(map(
            lambda res: GroupToSubject(**res),
            db.execute('SELECT group_name, subject_name, number_of_hours FROM group_to_subject')
        ))

almost_orm = AlmostOrm()