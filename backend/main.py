from functools import reduce
import backend_api
from flask import Flask, Response, json, g
# from database import PointSource, User, Repository, init_db
import database
from sqlalchemy import Sequence, select, Engine
from sqlalchemy.orm import Session
from points import calculate_points
import points
from data_structure import Repos, Repo, Commit

db_engine = None

def create_app():
    app = Flask(__name__)

    global db_engine
    if db_engine is None:
        db_engine = database.init_db()
        database.Base.metadata.create_all(db_engine)
            
    return app

app = create_app()


# Query point sources for the user and the repository
def find_point_sources_for(user, repository=None):
    engine = db_engine
    with Session(engine, expire_on_commit=False) as session:
        stmt = select(database.PointSource).join(database.PointSource.user).join(database.PointSource.repo).where(database.User.name == user)
        if repository is not None:
            stmt = stmt.where(database.Repository.name == repository)

        result = session.execute(stmt).all()
        return result

# Find all repositories that are associated with a given user
def find_repositories_for(user):
    engine = db_engine
    with Session(engine) as session:
        stmt = select(database.Repository).join(database.PointSource.user).join(database.PointSource.repo).where(database.User.name == user)
        
        result = session.execute(stmt).all()
        return result

def populate_user_if_needed(username):
    engine = db_engine
    with Session(engine) as session:
        stmt = select(database.User).where(database.User.name == username)

        exists = session.execute(stmt).first()
        if not exists:
            events = backend_api.get_user_events(username)
            print(events)
            database.load_events_to_db(engine, username, events)

@app.route("/")
def hello_world():
    return "<p>Hello</p>"

@app.route("/users/<username>/point_list", methods=['GET'])
def get_point_sources(username):
    engine = db_engine
    repos = backend_api.get_repos(username)
    if len(repos) > 0:
        database.load_repos_to_db(engine, repos)

    populate_user_if_needed(username)
    point_sources = find_point_sources_for(username)
    table = [
            {"points": round(100 * item[0].points * points.time_attentuation(points.days_since(item[0].time))), 
             "point_type": item[0].point_type,
             "repository": item[0].repo.name
             } for item in point_sources]
    response = Response(json.dumps(table))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response
    

@app.route("/users/<username>/total_points", methods=['GET'])
def get_user_points(username):
    point_sources = find_point_sources_for(username)

    total_points = points.calculate_points(map(lambda a: a[0], point_sources))

    response = Response(json.dumps({
        "user": username,
        "points": total_points,
        }))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response

@app.route("/users/<username>/repositories/info", methods=['GET'])
def get_user_repositories(username):
    engine = db_engine
    with Session(engine) as session:
        # Check if user exists and has associated repositories
        user = session.query(database.User).filter_by(name=username).first()
        if not user or len(user.repositories_info) == 0:
            # If no user or no repositories, fetch and store repo info
            return fetch_and_store_repo_info(username)

    # If user and repositories exist, return the stored info
    info_list = []
    for user_repo in user.repositories_info:
        repo = user_repo.repository
        info_list.append({
            "name": repo.name,
            "stars": repo.stars,
            "watchers": repo.watchers,
            "open_issues": repo.open_issues,
            "forks": repo.forks,
            "contributors": repo.contributors,
            "commits": repo.commits,
            "prs": repo.prs,
            "issues": repo.issues,
        })

    response = Response(json.dumps({
        "user": username,
        "repositories": info_list,
    }))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response



def fetch_and_store_repo_info(username):
    info_list = []

    repositories = find_repositories_for(username)
    for (repo,) in repositories:
        info_list.append({
            "name": repo.name,
            "stars": repo.stars,
            "watchers": repo.watchers,
            "open_issues": repo.open_issues,
            "forks": repo.forks,
            "contributors": repo.contributors,
            "commits": repo.commits,
            "prs": repo.prs,
            "issues": repo.issues,
        })

    response = Response(json.dumps({
        "user": username,
        "repositories": info_list,
    }))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


@app.route("/users/<username>/repositories", methods=['GET'])
def get_user_repositories_info(username):
    repositories = find_repositories_for(username)
    point_table = dict()
    for (repository,) in repositories:
        point_table[repository.name] = points.calculate_points(map(lambda a: a[0], find_point_sources_for(username, repository.name)))

    response = Response(json.dumps({
        "user": username,
        "repositories": point_table        
        }))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response

@app.route("/repositories", methods=['GET'])
def get_repository_list():
    engine = db_engine
    repositories = database.get_repo_list(engine)

    score_fn = lambda repo: (repo.stars + repo.forks + repo.watchers + (repo.open_issues / 5))

    data = [{"name": repo.name, "stars": repo.stars, "forks": repo.forks, "watchers": repo.watchers, "open_issues": repo.open_issues} for (repo,) in sorted(repositories, key=lambda repo: score_fn(repo[0]), reverse=True)]

    response = Response(json.dumps(data));
    response.headers["Access-Control-Allow-Origin"] = "*"


    return response

@app.route("/leaderboard", methods=['GET'])
def get_leaderboard():
    engine = db_engine

    leaderboard = database.point_leaderboard(engine)

    data = [(a, b) for ((a,), b) in leaderboard]

    data.sort(key=lambda a: a[1], reverse=True)

    response = Response(json.dumps(data));
    response.headers["Access-Control-Allow-Origin"] = "*"


    return response
