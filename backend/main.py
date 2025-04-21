import backend_api
from flask import Flask, Response, json
# from database import PointSource, User, Repository, init_db
import database
from sqlalchemy import select
from sqlalchemy.orm import Session
import points
from flask_cors import CORS
import os
import requests
from data_structure import Repos

db_engine = None

def create_app():
    app = Flask(__name__)
    CORS(app)

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
        user = session.query(database.User).filter_by(name=username).first()

        if not user or len(user.repositories_info) == 0:
            return fetch_and_store_repo_info(username)

        incomplete_repos = []
        for user_repo in user.repositories_info:
            repo = user_repo.repository
            if (
                repo.commits is None or
                repo.contributors is None or
                repo.prs is None or
                repo.issues is None or
                repo.stars is None or
                repo.watchers is None or
                repo.open_issues is None or
                repo.forks is None
            ):
                incomplete_repos.append(repo.name)

        if len(incomplete_repos) > 0:
            return fetch_and_store_repo_info(username)

        # If all required fields exist, return from database
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

        print('tomato')
        print(info_list)

        response = Response(json.dumps({
            "user": username,
            "repositories": info_list,
        }))
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    
def fetch_and_store_repo_info(username):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"
    }

    response = requests.get(url, headers=headers)    
    data = response.json()

    info_list = []

    # Create repos class
    repos = Repos()

    for repo in data:
        repos.add_repo(repo)

    repos_list = repos.get_repos()

    # --- ADDED: Start DB session ---
    engine = db_engine
    with Session(engine) as session:
        user = session.query(database.User).filter_by(name=username).first()
        if not user:
            user = database.User(name=username, github_username=username, clerk_hash="")
            session.add(user)
            session.commit()
    # --- END DB setup ---

    for repo in repos_list:
        # --- ADDED: Store repo metadata ---
        with Session(engine) as session:
            existing_repo = session.query(database.RepositoryInfo).filter_by(name=repo.name).first()
            if not existing_repo:
                existing_repo = database.RepositoryInfo(
                    name=repo.name,
                    stars=repo.get_stars(),
                    watchers=repo.get_watchers(),
                    open_issues=repo.get_open_issues(),
                    forks=repo.get_forks(),
                    contributors=repo.get_total_contributors(),
                    commits=repo.get_total_commits(),
                    prs=repo.get_total_prs(),
                    issues=repo.get_total_issues()
                )
                session.add(existing_repo)
                session.commit()

            link = session.query(database.UserRepository).filter_by(
                user_id=user.id,
                repo_id=existing_repo.id
            ).first()
            if not link:
                session.add(database.UserRepository(user_id=user.id, repo_id=existing_repo.id))
                session.commit()
        # --- END DB insert ---

        info_list.append({
            "name": repo.name,
            "stars": repo.get_stars(),
            "watchers": repo.get_watchers(),
            "open_issues": repo.get_open_issues(),
            "forks": repo.get_forks(),
            "contributors": repo.get_total_contributors(),
            "commits": repo.get_total_commits(),
            "prs": repo.get_total_prs(),
            "issues": repo.get_total_issues(),
        })

    response = Response(json.dumps({
        "user": username,
        "repositories": info_list,
    }))
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response
    
@app.route("/users/<username>/repositories/info/popular", methods=['GET'])
def get_popular_repositories(username):
    engine = db_engine
    with Session(engine) as session:
        popular_repos = session.query(database.PopularRepositoryInfo).all()

        # If no popular repos or incomplete data, fetch and store
        if not popular_repos or any(
            repo.stars is None or repo.forks is None or repo.watchers is None or
            repo.open_issues is None or repo.commits is None or
            repo.contributors is None or repo.prs is None or repo.issues is None
            for repo in popular_repos
        ):
            return fetch_and_store_popular_repos(username)

        # Format and return
        info_list = [{
            "name": repo.name,
            "stars": repo.stars,
            "watchers": repo.watchers,
            "open_issues": repo.open_issues,
            "forks": repo.forks,
            "contributors": repo.contributors,
            "commits": repo.commits,
            "prs": repo.prs,
            "issues": repo.issues,
        } for repo in popular_repos]

        response = Response(json.dumps({
            "user": username,
            "repositories": info_list,
        }))
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    
def fetch_and_store_popular_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"
    }

    response = requests.get(url, headers=headers)    
    data = response.json()

    # Create repos class
    repos = Repos()

    for repo in data:
        repos.add_repo(repo)

    engine = db_engine
    with Session(engine) as session:

        ranked_repos = repos.get_popular_repos_ranked()

        # Clear old data
        session.query(database.PopularRepositoryInfo).delete()

        for repo in ranked_repos:
            popular = database.PopularRepositoryInfo(
                name=repo.name,
                stars=repo.get_stars() or 0,
                forks=repo.get_forks() or 0,
                watchers=repo.get_watchers() or 0,
                open_issues=repo.get_open_issues() or 0,
                contributors=repo.get_total_contributors() or 0,
                commits=repo.get_total_commits() or 0,
                prs=repo.get_total_prs() or 0,
                issues=repo.get_total_issues() or 0
            )
            session.add(popular)

        session.commit()

    # Return the same response format
    info_list = [{
        "name": repo.name,
        "stars": repo.get_stars() or 0,
        "watchers": repo.get_watchers() or 0,
        "open_issues": repo.get_open_issues() or 0,
        "forks": repo.get_forks() or 0,
        "contributors": repo.get_total_contributors() or 0,
        "commits": repo.get_total_commits() or 0,
        "prs": repo.get_total_prs() or 0,
        "issues": repo.get_total_issues() or 0,
    } for repo in ranked_repos]

    response = Response(json.dumps({
        "user": username,
        "repositories": info_list,
    }))
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/users/<username>/repositories/info/oldest", methods=['GET'])
def get_oldest_repositories(username):
    engine = db_engine
    with Session(engine) as session:
        oldest_repos = session.query(database.OldestRepositoryInfo).all()

        # If no oldest repos or incomplete data, fetch and store
        if not oldest_repos or any(
            repo.stars is None or repo.forks is None or repo.watchers is None or
            repo.open_issues is None or repo.commits is None or
            repo.contributors is None or repo.prs is None or repo.issues is None
            for repo in oldest_repos
        ):
            return fetch_and_store_oldest_repos(username)

        # Format and return
        info_list = [{
            "name": repo.name,
            "stars": repo.stars,
            "watchers": repo.watchers,
            "open_issues": repo.open_issues,
            "forks": repo.forks,
            "contributors": repo.contributors,
            "commits": repo.commits,
            "prs": repo.prs,
            "issues": repo.issues,
        } for repo in oldest_repos]

        response = Response(json.dumps({
            "user": username,
            "repositories": info_list,
        }))
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    
def fetch_and_store_oldest_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"
    }

    response = requests.get(url, headers=headers)    
    data = response.json()

    # Create repos class
    repos = Repos()

    for repo in data:
        repos.add_repo(repo)

    engine = db_engine
    with Session(engine) as session:

        ranked_repos = repos.get_old_repos_ranked()

        # Clear old data
        session.query(database.OldestRepositoryInfo).delete()

        for repo in ranked_repos:
            oldest = database.OldestRepositoryInfo(
                name=repo.name,
                stars=repo.get_stars() or 0,
                forks=repo.get_forks() or 0,
                watchers=repo.get_watchers() or 0,
                open_issues=repo.get_open_issues() or 0,
                contributors=repo.get_total_contributors() or 0,
                commits=repo.get_total_commits() or 0,
                prs=repo.get_total_prs() or 0,
                issues=repo.get_total_issues() or 0
            )
            session.add(oldest)

        session.commit()

    # Return the same response format
    info_list = [{
        "name": repo.name,
        "stars": repo.get_stars() or 0,
        "watchers": repo.get_watchers() or 0,
        "open_issues": repo.get_open_issues() or 0,
        "forks": repo.get_forks() or 0,
        "contributors": repo.get_total_contributors() or 0,
        "commits": repo.get_total_commits() or 0,
        "prs": repo.get_total_prs() or 0,
        "issues": repo.get_total_issues() or 0,
    } for repo in ranked_repos]

    response = Response(json.dumps({
        "user": username,
        "repositories": info_list,
    }))
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/users/<username>/repositories/info/activity", methods=['GET'])
def get_activity_repositories(username):
    engine = db_engine
    with Session(engine) as session:
        activity_repos = session.query(database.ActivityRepositoryInfo).all()

        # If no oldest repos or incomplete data, fetch and store
        if not activity_repos or any(
            repo.stars is None or repo.forks is None or repo.watchers is None or
            repo.open_issues is None or repo.commits is None or
            repo.contributors is None or repo.prs is None or repo.issues is None
            for repo in activity_repos
        ):
            return fetch_and_store_activity_repos(username)

        # Format and return
        info_list = [{
            "name": repo.name,
            "stars": repo.stars,
            "watchers": repo.watchers,
            "open_issues": repo.open_issues,
            "forks": repo.forks,
            "contributors": repo.contributors,
            "commits": repo.commits,
            "prs": repo.prs,
            "issues": repo.issues,
        } for repo in activity_repos]

        response = Response(json.dumps({
            "user": username,
            "repositories": info_list,
        }))
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    
def fetch_and_store_activity_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"
    }

    response = requests.get(url, headers=headers)    
    data = response.json()

    # Create repos class
    repos = Repos()

    for repo in data:
        repos.add_repo(repo)

    engine = db_engine
    with Session(engine) as session:

        ranked_repos = repos.get_active_repos_ranked()

        # Clear old data
        session.query(database.ActivityRepositoryInfo).delete()

        for repo in ranked_repos:
            activity = database.ActivityRepositoryInfo(
                name=repo.name,
                stars=repo.get_stars() or 0,
                forks=repo.get_forks() or 0,
                watchers=repo.get_watchers() or 0,
                open_issues=repo.get_open_issues() or 0,
                contributors=repo.get_total_contributors() or 0,
                commits=repo.get_total_commits() or 0,
                prs=repo.get_total_prs() or 0,
                issues=repo.get_total_issues() or 0
            )
            session.add(activity)

        session.commit()

    # Return the same response format
    info_list = [{
        "name": repo.name,
        "stars": repo.get_stars() or 0,
        "watchers": repo.get_watchers() or 0,
        "open_issues": repo.get_open_issues() or 0,
        "forks": repo.get_forks() or 0,
        "contributors": repo.get_total_contributors() or 0,
        "commits": repo.get_total_commits() or 0,
        "prs": repo.get_total_prs() or 0,
        "issues": repo.get_total_issues() or 0,
    } for repo in ranked_repos]

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
