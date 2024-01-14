from flask import Flask, render_template, request
from music_libs import Yandex, find_same

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/submit")
def music():
    user1_id = request.args.get("user1_id", "")
    user1 = Yandex.User(user1_id)
    user2_id = request.args.get("user2_id", "")
    user2 = Yandex.User(user2_id)
    users = {user1, user2}
    result = sorted(list(find_same.tracks(*users)))
    return render_template("answer.html", result=result)


app.run()
