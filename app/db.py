import os
import psycopg2
from sqlalchemy import create_engine

def db_connection(url):
    engine = create_engine(str(url))
    return engine