from flask import *
from flask_sqlalchemy import *
from flask_login import *
from operator import itemgetter
import datetime
import time
import hashlib
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)

# Flask-SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ranking.db"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = "q\x17eOG\x15\x9a\xcb\xe1a\x96\xb3\x16Hd\x8f\xd3\x04v\xc0m\x846\x1a'"

gradyear = 12
events = ["100m Dash", "200m Dash", "400m Dash", "800m Run", "1600m Run", "3200m Run", "3000m Steeple", "110HH", "400IH", "4x100m", "4x200m", "4x400m", "4x800m", "HJ", "PV", "LJ", "TJ", "SP", "DT", "Pent"]
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

class User(db.Model):
    __tablename__ = "users"
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    id = db.Column(primary_key=True)
    def __init__(self, username, password, id):
        self.username = username
        self.password = password
        self.id = id

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

db.create_all()

@app.route("/", methods = ["GET"])
def index():
    return render_template("index.html")

@app.route("/schoolrecords", methods = ["GET", "POST"])
def schoolrecords():
    return render_template("schoolrecords.html")

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

@app.route("/data_entry", methods = ["GET", "POST"])
@login_required
def data_entry():
    if request.method == "POST":
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        event = request.form.get("eventselect")
        year = request.form.get("year")
        meet = request.form.get("meet")
        performance = request.form.get("performance")
        if fname != "" and lname != "" and event != "Choose..." and year != "" and performance != "":
            if meet == "":
                meet = "unknown"
            rows = Performance.query.all()
            newrows = sorted(rows, key=lambda x:x.performance_id, reverse = True)
            first = newrows[0]
            performance_id = first.performance_id + 1
            db.session.add(Performance(lname, fname, year, performance, event, meet, gradyear, performance_id))
            db.session.commit()
        return redirect(url_for("rankings"))
    else:
        return render_template("data_entry.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("login.html", error = "missing username or password")
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username=username)
            if user == None:
                return render_template("failure.html")
            currentuser = user[0]
            if  pbkdf2_sha256.verify(password, currentuser.password) == True:
                login_user(currentuser)
                return redirect(url_for("data_entry"))
            else:
                return render_template("failure.html")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("register.html")
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            password = pbkdf2_sha256.hash(password)
            newuser = User(username, password, 1)
            db.session.add(newuser)
            db.session.commit()
            return redirect(url_for("data_entry"))
    else:
        return render_template("register.html")

def rowsort(rows, event):
    rowscopy = rows
    # sort rows from best to worst, determine whether the event to rank is a track or field event to decide to go by
    # smallest to largest or vice-versa
    if event not in field_events:
        for row in rowscopy:
            mark = row.performance
            if mark == "":
                return None
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
                if mark == "":
                    return None
                feet = mark.split("-")[0]
                inches = mark.split("-")[1]
                tot_height = (int(feet) * 12) + float(inches)
                row.performance = str(tot_height)
            newrows = sorted(rowscopy, key=lambda x:x.performance, reverse=True)
            for row in rowscopy:
                if row.firstname == "NA":
                    row.firstname = ""
                height = float(row.performance)
                feet = int(height / 12)
                inches = height % 12
                newheight = "{}-{:05.2f}".format(feet, inches)
                row.performance = str(newheight)
        else:
            newrows = sorted(rowscopy, key=lambda x:x.performance, reverse=True)
    return newrows

@login_manager.user_loader
def load_user(id):
    try:
        return User.query.get(id)
    except:
        return none
