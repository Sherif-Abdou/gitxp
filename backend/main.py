from flask import Flask, Response, json
from database import PointSource, User
from sqlalchemy import Sequence, select

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello</p>"

@app.route("/users/<username>/points", methods=['GET'])
def get_user_points(username):
    user = select(User).where(User.name.in_([username]))
    print(user)

    points = select(PointSource).join(PointSource.user).where(User.name.in_([username]))
    print(points)

    response = Response(json.dumps({
        "user": username,
        "points": 72,
        }))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response

@app.route("/users/<username>/repositories", methods=['GET'])
def get_user_repositories(username):
    response = Response(json.dumps({
        "user": username,
        "repositories": {
            "imxrt-rt": 71,
            "test": 1,
            },
        }))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response

