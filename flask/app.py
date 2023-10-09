import find_same

# import get_user
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/submit")
def music():
    user1_id = request.args.get("user1_id", "")
    user2_id = request.args.get("user2_id", "")
    users = {user1_id, user2_id}
    result = sorted(list(find_same.tracks(*users)))
    return render_template("answer.html", result=result)