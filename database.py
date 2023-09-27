'''import psycopg2

#if use cursor => conn.cursor()
conn = psycopg2.connect(
    host="localhost",
    database="diaspo_django",
    user="postgres",
    password="root",
    port="5432"
)
'''
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy_utils import create_database, database_exists

#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root@127.0.0.1:5432/fafana"
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root@127.0.0.1:5432/diaspo_django8"
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root@192.168.88.213:5432/diaspo_django8"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123Server2012.@192.168.88.213:6532/diaspo_django8"
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root@paositrasiege.mg:5432/diaspo_django3"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Create the database if it doesn't exist
if not database_exists(SQLALCHEMY_DATABASE_URL):
    create_database(SQLALCHEMY_DATABASE_URL)

# Create the tables in the database using Alembic
#Base.metadata.create_all(engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
