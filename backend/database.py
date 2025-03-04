from datetime import datetime
from typing import List
from sqlalchemy import create_engine, String, ForeignKey, Integer, DateTime, select
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

class Base(DeclarativeBase):
    pass

# Basic user information stored within the database
class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    github_username: Mapped[str] = mapped_column(String(30))

    points: Mapped[List["PointSource"]] = relationship(
            back_populates="user", cascade="all, delete-orphan"
            )

# Represents a point source in the database
# Every source of points is stored individually so points over time can be calculated
class PointSource(Base):
    __tablename__ = "points"

    id: Mapped[int] = mapped_column(primary_key=True)
    points: Mapped[int] = mapped_column(Integer())
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    time: Mapped[datetime] = mapped_column(DateTime(), server_default = sqlalchemy.func.now())

    user: Mapped["User"] = relationship(back_populates="points")

def populate_points_for(engine, user):
    print(f"\n\nUser id: {user.id}\n\n")
    with Session(engine) as session:
        point_source_a = PointSource(
                id = 0,
                points = 5,
                user_id = user.id,
                )
        point_source_b = PointSource(
                id = 1,
                points = 5,
                user_id = user.id,
                )

        session.add_all([point_source_a, point_source_b])
        session.commit()


if __name__ == "__main__":
    engine = create_engine('postgresql+psycopg2://sherif:password@localhost:5432/postgres', echo=True)
    user = None
    with Session(engine) as session:
        stmt = select(User).where(User.name.in_(["sherif"]))

        user = session.execute(stmt).one()

        populate_points_for(engine, user)
    # Base.metadata.create_all(engine)


