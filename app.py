from flask import Flask, render_template

app = Flask(__name__)
from db import db
from views import AdminView, ScheduleView


@app.route('/')
def hello_world():
    return render_template('index.html')


app.add_url_rule('/admin', view_func=AdminView.as_view('admin'))
app.add_url_rule('/schedule', view_func=ScheduleView.as_view('schedule'))


if __name__ == '__main__':
    app.run()
