import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine = None

try:
    engine = create_engine('postgresql://matias92:francia92@localhost:5432/exchanges_db')
    with engine.connect():
        pass
except:
    engine = create_engine(database_url)
    
print(engine.url)