from flask import *
from sqlalchemy import *

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/rankings")
def rankings():
    return render_template("rankings.html")

@app.route("/ranklookup")
def ranklookup():
    data = request.args.get("q")
    parameters = data.split(",")

    return jsonify(ranks)
