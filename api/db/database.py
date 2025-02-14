from core import config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()

encoded_password = urllib.parse.quote(config.passwordDB)

DATABASE_URI = f"postgresql://{config.usernameDB}:{encoded_password}@{config.servernameDB}:5432/{config.databasenameDB}?sslmode=require"

engine = create_engine("postgresql://adminuser:eM]Pc84R<W2o@psql-dev-corp-finsa.postgres.database.azure.com:5432/db-dev-corp-finsa")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


