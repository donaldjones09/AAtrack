from flask import *
from flask_sqlalchemy import SQLAlchemy

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
        event = request.form.get("eventselect")
        grade = request.form.get("gradeselect")
        year = request.form.get("yearselect")
        rows = Performance.query.all()
        return render_template("rankings.html", rows = rows)
    else:
        return render_template("rankings.html")
