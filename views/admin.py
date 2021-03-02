import typing as t
from collections import namedtuple

from flask import render_template
from flask.views import View

from almost_orm import almost_orm



class AdminView(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        return render_template(
            'admin.html',
            groups=almost_orm.groups,
            teachers=almost_orm.teachers,
            classrooms=almost_orm.classrooms,
            subjects=almost_orm.subjects,
            teacher_to_subject=almost_orm.teacher_to_subject,
            group_to_subject=almost_orm.group_to_subject,
        )

