
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./healthcare.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} # Manage the connection to the database
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
) # Session factory for executing operations

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()