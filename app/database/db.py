from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# Create a database engine
engine = create_engine('sqlite:///parenting_bot.db')

# Declare a base class for database models
Base = declarative_base()
