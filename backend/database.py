from datetime import datetime
from typing import List
from sqlalchemy import create_engine, String, ForeignKey, Integer, DateTime, select
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from os import getenv
from dotenv import load_dotenv

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
    name: Mapped[str] = mapped_column(String(30))
    stars: Mapped[int] = mapped_column(Integer())


# Represents a point source in the database
# Every source of points is stored individually so points over time can be calculated
class PointSource(Base):
    __tablename__ = "points"

    id: Mapped[int] = mapped_column(primary_key=True)
    points: Mapped[int] = mapped_column(Integer())
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    repo_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    time: Mapped[datetime] = mapped_column(DateTime(), server_default = sqlalchemy.func.now())

    user: Mapped["User"] = relationship(back_populates="points")
    repo: Mapped["Repository"] = relationship()

# Populates some fake points entries in the database
def populate_points_for(engine, user_id, repo_id):
    print(f"\n\nUser id: {user_id}\n\n")
    with Session(engine) as session:
        point_source_a = PointSource(
                points = 5,
                user_id = user_id,
                repo_id = repo_id,
                )
        point_source_b = PointSource(
                points = 5,
                user_id = user_id,
                repo_id = repo_id,
                )

        session.add_all([point_source_a, point_source_b])
        session.commit()

def init_db():
    load_dotenv()
    db_url = getenv("POSTGRES_DB")
    assert (db_url is not None)
    engine = create_engine(db_url, echo=True)
    return engine

if __name__ == "__main__":
    engine = init_db()
    # Base.metadata.create_all(engine)
    populate_points_for(engine, 1, 1)


