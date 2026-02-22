from sqlmodel import SQLModel, create_engine, Session
from db_loader import make_bio_instances, make_stats_instances
from models import Bio, Stats

engine = create_engine("sqlite:///hurst_hockey.db")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    bios = make_bio_instances("bio.csv")
    session.add_all(bios)
    session.commit()

    stats = make_stats_instances("stats.csv")
    session.add_all(stats)
    session.commit()
