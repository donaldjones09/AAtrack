from flask import *
from sqlalchemy import *

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/rankings")
def rankings():
    return render_template("rankings.html")

"""look up rankings of given parameters, return DB rows as JSON array"""
"""
@app.route("/ranklookup")
def ranklookup():
    data = request.args.get("q")
    parameters = data.split(",")
    #will return a json array called ranks to script.js to update rankings page
    return jsonify(ranks)
"""
