import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))

            print(
                "Database connected successfully:",
                result.scalar()
            )

    except Exception as e:
        print(
            "Database connection failed:",
            e
        )