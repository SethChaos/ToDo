from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#the configuration for the database connection.
DATABASE_URL = "mysql+pymysql://admin:admin@localhost:3306/todo"

#creating the engine
#the engine is the object that manages the connection to the database
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from models import Base
    Base.metadata.create_all(bind=engine)
#this function creates the tables in the database