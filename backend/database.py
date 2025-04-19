from datetime import datetime
from typing import Iterator, List
from sqlalchemy import create_engine, String, ForeignKey, Integer, DateTime, select, update
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from os import getenv
from dotenv import load_dotenv

import points
from backend_api import *

class Base(DeclarativeBase):
    pass

# Basic user information stored within the database
class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    github_username: Mapped[str] = mapped_column(String(30))
    clerk_hash: Mapped[str] = mapped_column(String(80))

    points: Mapped[List["PointSource"]] = relationship(
            back_populates="user", cascade="all, delete-orphan"
            )

class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(70))
    stars: Mapped[int] = mapped_column(Integer())
    forks: Mapped[int] = mapped_column(Integer())
    watchers: Mapped[int] = mapped_column(Integer())
    open_issues: Mapped[int] = mapped_column(Integer())


# Represents a point source in the database
# Every source of points is stored individually so points over time can be calculated
class PointSource(Base):
    __tablename__ = "points"

    # Primary key of the point source
    id: Mapped[int] = mapped_column(primary_key=True)
    # Number of points this was originally worth, not including attentuation
    points: Mapped[int] = mapped_column(Integer())
    # Description of the way points were earned
    point_type: Mapped[str] = mapped_column(String(30))
    # Time when the point event occured
    time: Mapped[datetime] = mapped_column(DateTime(), server_default = sqlalchemy.func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    repo_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))

    user: Mapped["User"] = relationship(back_populates="points")
    repo: Mapped["Repository"] = relationship(lazy='subquery')

# Populates some fake points entries in the database
def populate_points_for(engine, user_id, repo_id):
    print(f"\n\nUser id: {user_id}\n\n")
    with Session(engine) as session:
        point_source_a = PointSource(
                points = 5,
                point_type = "Commit",
                user_id = user_id,
                repo_id = repo_id,
                )
        point_source_b = PointSource(
                points = 5,
                point_type = "Commit",
                user_id = user_id,
                repo_id = repo_id,
                )

        session.add_all([point_source_a, point_source_b])
        session.commit()

def get_point_type(point):
    if isinstance(point, points.CommitEvent):
        return "Commit"
    if isinstance(point, points.OpenIssueEvent):
        return "Issue"
    if isinstance(point, points.CreateRepoEvent):
        return "Repo"
    if isinstance(point, points.ClosePullRequestEvent):
        return "PR"
    if isinstance(point, points.OpenPullRequestEvent):
        return "PR"
    return "Other"

def load_repos_to_db(engine, repos):
    with Session(engine) as session:
        to_add = []
        to_update = []
        for repo in repos:
            present = session.query(Repository.name).filter_by(name=repo.name).first() is not None
            if present:
                to_update.append(update(Repository).where(Repository.name==repo.name).values(stars=repo.stars, forks=repo.forks, watchers=repo.watchers, open_issues=repo.open_issues))
            else:
                to_add.append(repo)

        session.add_all(to_add)
        for u in to_update:
            session.execute(u)

        session.commit()

def load_events_to_db(engine, username, events):
    with Session(engine) as session:
        user = session.execute(select(User).where(User.name == username)).first()
        if user is None:
            user = (User(name=username, github_username=username, clerk_hash=""),)
            session.add(user[0])
            session.commit()
        for event in events:
            repo_item = session.execute(select(Repository).where(Repository.name == event.repo)).first()
            if not repo_item:
                session.add(Repository(name=event.repo, stars=0, forks=0, watchers=0, open_issues=0))
                session.commit()
        session.commit()
        for event in events:
            repo_item = session.execute(select(Repository).where(Repository.name == event.repo)).first()
            if not session.execute(select(PointSource).where(PointSource.time == event.timestamp)).first():
                source = PointSource(
                        points = event.generate_points(),
                        point_type = get_point_type(event),
                        time = event.timestamp,
                        repo_id = repo_item[0].id,
                        user_id = user[0].id,
                        )
                session.add(source)
        session.commit()

def get_repo_list(engine):
    with Session(engine) as session:
        stmt = select(Repository)
        items = session.execute(stmt).all()

        return items

def init_db(echo=True):
    load_dotenv()
    db_url = getenv("POSTGRES_DB")
    assert (db_url is not None)
    engine = create_engine(db_url, echo=echo)
    return engine

if __name__ == "__main__":
    engine = init_db()
    Base.metadata.create_all(engine)
    # populate_points_for(engine, 1, 1)
    # events = get_user_events("https://api.github.com/users/danushsingla/events")
    # print(events)
    # load_events_to_db("danushsingla", events)

