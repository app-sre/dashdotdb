import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(os.environ['DASHDOTDB_DATABASE_URL'])
Session = sessionmaker(bind=engine)()
