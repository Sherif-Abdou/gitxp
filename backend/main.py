from functools import reduce
from flask import Flask, Response, json, g
from database import PointSource, User, Repository, init_db
from sqlalchemy import Sequence, select, Engine
from sqlalchemy.orm import Session
from points import calculate_points

db_engine = None

def create_app():
    app = Flask(__name__)

    global db_engine
    if db_engine is None:
        db_engine = init_db()
            
    return app

app = create_app()


# Query point sources for the user and the repository
def find_point_sources_for(user, repository=None):
    engine = db_engine
    with Session(engine) as session:
        stmt = select(PointSource).join(PointSource.user).join(PointSource.repo).where(User.name == user)
        if repository is not None:
            stmt = stmt.where(Repository.name == repository)

        result = session.execute(stmt).all()
        return result

# Find all repositories that are associated with a given user
def find_repositories_for(user):
    engine = db_engine
    with Session(engine) as session:
        stmt = select(Repository).join(PointSource.user).join(PointSource.repo).where(User.name == user)
        
        result = session.execute(stmt).all()
        return result

@app.route("/")
def hello_world():
    return "<p>Hello</p>"

@app.route("/users/<username>/points", methods=['GET'])
def get_user_points(username):
    point_sources = find_point_sources_for(username)

    total_points = calculate_points(map(lambda a: a[0], point_sources))

    response = Response(json.dumps({
        "user": username,
        "points": total_points,
        }))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response

@app.route("/users/<username>/repositories", methods=['GET'])
def get_user_repositories(username):
    repositories = find_repositories_for(username)
    point_table = dict()
    for (repository,) in repositories:
        point_table[repository.name] = calculate_points(map(lambda a: a[0], find_point_sources_for(username, repository.name)))

    response = Response(json.dumps({
        "user": username,
        "repositories": point_table        
        }))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response

