import typing as t
import urllib
from collections import defaultdict

from urllib.parse import quote as quote_uri

from flask import request, render_template
from flask.views import View
from almost_orm import almost_orm
from solvers.solver import get_full_schedule


class ScheduleView(View):
    methods = ['GET', 'POST']

    
    def dispatch_request(self):
        group = request.args.get('group')
        solver = request.args.get('solver', 'stasian')
        kwargs = dict(
            group=group,
            groups=almost_orm.groups,
            quote_uri=quote_uri,
            solver=solver,
            solution_links=self.get_possible_solution_links(),
        )
        if group:
            kwargs['schedule'] = self.get_schedule(solver, group=group)
        return render_template(
            'schedule.html',
            **kwargs
        )
    
    def get_possible_solution_links(self):
        args = request.args.copy()
        res = dict()
        for solver in ['mariia', 'stasian', 'stasian_1']:
            args['solver'] = solver
            res[solver] = urllib.parse.urlencode(args)
        return res

    def get_schedule(self, solver, group) -> t.Dict[t.Tuple[int, int], t.List[t.Tuple[str, str, str]]]:
        schedule = get_full_schedule(solver)
        result = defaultdict(list)
        for entity in schedule:
            if entity.group == group:
                result[(entity.day, entity.pair)].append((entity.classroom, entity.subject, entity.teacher))
        return result
