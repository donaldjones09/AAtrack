from flask import *
from flask_sqlalchemy import *
from operator import itemgetter
import datetime
import time

app = Flask(__name__)

# Flask-SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ranking.db"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

field_events = ["HJ", "PV", "LJ", "TJ", "SP", "DT", "Pent"]

class Performance(db.Model):
    __tablename__ = "performances"
    lastname = db.Column(db.String(100))
    firstname = db.Column(db.String(100))
    date = db.Column(db.String(100))
    performance = db.Column(db.String(100))
    event = db.Column(db.String(100))
    meet = db.Column(db.String(100))
    graduationyear = db.Column(db.Integer)
    performance_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, lastname, firstname, date, performance, event, meet, graduationyear, performance_id):
        self.lastname = lastname
        self.firstname = firstname
        self.date = date
        self.performance = performance
        self.event = event
        self.meet = meet
        self.graduationyear = graduationyear
        self.performance_id = performance_id

db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/rankings", methods = ["GET", "POST"])
def rankings():
    if request.method == "POST":
        #if no event is selected return a blank page
        if request.form.get("eventselect") == "":
            return render_template("rankings.html")
        event = request.form.get("eventselect")
        #if a year is selected filter results using it
        if not request.form.get("yearselect") == "Choose...":
            year = request.form.get("yearselect")
            originalrows = Performance.query.filter_by(event=event, date=year)
        else:
            originalrows = Performance.query.filter_by(event=event)
        rows = rowsort(originalrows, event)
        return render_template("rankings.html", event=event, rows = rows)
    else:
        return render_template("rankings.html")

def rowsort(rows, event):
    rowscopy = rows
    # sort rows from best to worst, determine whether the event to rank is a track or field event to decide to go by
    # smallest to largest or vice-versa
    if event not in field_events:
        for row in rowscopy:
            mark = row.performance
            if ':' in mark:
                minutes = mark.split(':')[0]
                seconds = mark.split(':')[1]
                tot_seconds = (int(minutes) * 60) + float(seconds)
            else:
                seconds = mark.split(':')[0]
                tot_seconds = float(seconds)
            row.performance = str(tot_seconds)
        newrows = sorted(rowscopy, key=lambda x:x.performance)
        for row in rowscopy:
            time = float(row.performance)
            if time > 60:
                mins = round(time/60)
                seconds = time % 60
                newtime = "{}:{:05.2f}".format(mins, seconds)
                row.performance = str(newtime)
            else:
                seconds = time
                newtime = "{:05.2f}".format(seconds)
                row.performance = str(newtime)
            if row.firstname == "NA":
                row.firstname = ""
    else:
        if not event == "Pent":
            for row in rowscopy:
                mark = row.performance
                feet = mark.split("-")[0]
                inches = mark.split("-")[1]
                tot_height = (int(feet) * 12) + float(inches)
                row.performance = str(tot_height)
            newrows = sorted(rowscopy, key=lambda x:x.performance, reverse=True)
            for row in rowscopy:
                if row.firstname == "NA":
                    row.firstname = ""
                height = float(row.performance)
                feet = round(height / 12)
                inches = height % 12
                newheight = "{}-{:05.2f}".format(feet, inches)
                row.performance = str(newheight)
        else:
            newrows = sorted(rowscopy, key=lambda x:x.performance, reverse=True)
    return newrows
