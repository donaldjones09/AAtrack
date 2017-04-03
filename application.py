from flask import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Flask-SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ranking.db"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

class Performances():
    __tablename__ = "Performances"
    lastname = db.Column(db.Text)
    firstname = db.Column(db.Text)
    date = db.Column(db.Text)
    performace = db.Column(db.Text)
    event = db.Column(db.Text)
    meet = db.Column(db.Text)
    graduationyear = db.Column(db.Integer)


    def __init__(self, lastname, firstname, date, performance, event, meet, graduationyear):
        self.lastname = lastname
        self.firstname = firstname
        self.date = date
        self.performance = performance
        self.event = event
        self.meet = meet
        self.graduationyear = graduationyear


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/rankings", methods = ["GET", "POST"])
def rankings():
    if request.method == "GET":
        event = request.form.get("eventselect")
        grade = request.form.get("gradeselect")
        rows = Performances.query.filter_by(Performances.event == event).all()
        db.session.commit()
        return render_template("rankings.html", rows = rows)
    else:
        return render_template("rankings.html")
    return render_template("rankings.html")
