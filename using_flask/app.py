import music_libs.find_same as find_same
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/submit")
def music():
    user1_id = request.args.get("user1_id", "")
    user1 = find_same.User(user1_id)
    user2_id = request.args.get("user2_id", "")
    user2 = find_same.User(user2_id)
    users = {user1, user2}
    result = sorted(list(find_same.tracks(*users)))
    return render_template("answer.html", result=result)
