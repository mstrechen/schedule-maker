import typing as t

from almost_orm import almost_orm, TeacherToSubject, GroupToSubject


class Mapper:
    def __init__(self):
        self.groups = almost_orm.groups
        self.subjects = almost_orm.subjects
        self.teachers = almost_orm.teachers
        self.classrooms = almost_orm.classrooms
        self.teacher_to_subject = almost_orm.teacher_to_subject
        self.group_to_subject = almost_orm.group_to_subject

        self.id_to_group = {key: value.group_name for key, value in enumerate(self.groups)}
        self.group_to_id = {value.group_name: key for key, value in enumerate(self.groups)}
        self.id_to_subject = {key: value.subject_name for key, value in enumerate(self.subjects)}
        self.subject_to_id = {value.subject_name: key for key, value in enumerate(self.subjects)}
        self.id_to_teacher = {key: value.name for key, value in enumerate(self.teachers)}
        self.teacher_to_id = {value.name: key for key, value in enumerate(self.teachers)}
        self.id_to_classroom = {key: value.classroom_name for key, value in enumerate(self.classrooms)}
        self.classroom_to_id = {value.classroom_name: key for key, value in enumerate(self.classrooms)}

    @property
    def number_of_lectures(self):
        return sum(1 for s in self.subjects if s.is_lecture)

    @property
    def number_of_big_classrooms(self):
        return sum(1 for c in self.classrooms if c.is_for_lecture)

    def translate_teacher_to_subject(self, tts: t.List[TeacherToSubject]):
        return [
            (self.teacher_to_id[tts_record.name], self.subject_to_id[tts_record.subject_name])
            for tts_record in tts
        ]

    def translate_group_to_subject(self, gts: t.List[GroupToSubject]):
        return [
            (
                self.group_to_id[gts_record.group_name],
                self.subject_to_id[gts_record.subject_name],
                gts_record.number_of_hours
            )
            for gts_record in gts
        ]

    def parse_schedule(self, s: str):
        s = s.strip()
        # we don't really need 1st string
        lines = s.split('\n')[1:]
        res = [
            list(map(int, l.strip().split()))
            for l in lines
        ]
        return res

    def translate_schedule(self, schedule: t.List[t.Tuple[int, int, int, int, int, int]]):
        # (S, T, G, C, day_of_the_week:0-4, pair_number:0-3)

        return [
            (
                self.id_to_subject[subj], self.id_to_teacher[teacher],
                self.id_to_group[group], self.id_to_classroom[classroom],
                day, pair
            )
            for subj, teacher, group, classroom, day, pair in schedule
        ]


def get_mapper():
    return Mapper()

