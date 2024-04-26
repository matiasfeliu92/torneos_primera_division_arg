from fastapi import FastAPI,HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, exc, text as sql_text
from sqlalchemy.orm import sessionmaker
from decouple import config
from dotenv import load_dotenv
import sys
import os
import json

sys.path.append('C:\\Users\\PC\\Documents\\Matias\\torneos_primera_division_arg')
from utils import get_team_data
load_dotenv()

app = FastAPI()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)
print(engine.url)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

@app.get("/index")
def read_root():
    return {"Hello": "World"}

# global df_teams

@app.get("/teams/links")
def get_teams_links():
    df_teams = pd.DataFrame()
    try:
        with engine.connect() as conn:
            query = sql_text("SELECT * FROM torneos_primera_arg.url_equipos")
            df_result = pd.read_sql_query(query, conn)
            df_teams = pd.concat([df_teams, df_result], ignore_index=True)
            teams = df_teams.to_dict(orient='records')
            return JSONResponse(content=teams, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot find the request data: {str(e)}")
    
@app.get("/teams")
def get_teams():
    df_teams = pd.DataFrame()
    teams_matchs_data = []
    try:
        with engine.connect() as conn:
            query = sql_text("SELECT * FROM torneos_primera_arg.url_equipos")
            df_result = pd.read_sql_query(query, conn)
            df_teams = pd.concat([df_teams, df_result], ignore_index=True)
            df_teams['json_data'] = df_teams['json_data'].apply(json.loads)
            print("-----------------------------------json_data-------------------------------------------")
            for item in df_teams['json_data']:
                print(type(item))
                teams_matchs_data.append(item)  # Collect JSON data for all items
            return JSONResponse(content=teams_matchs_data, status_code=200)  # Return all JSON data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot find the request data: {str(e)}")
    
@app.post("/teams")
def post_teams(yearr: str, cod: str):
    yearr_list = [int(year) for year in yearr.split(', ')]
    cod_list = cod.split(', ')
    print("--------------------------yearr-------------------------")
    print(yearr_list)
    print("--------------------------cod-------------------------")
    print(cod_list)
    df_teams = pd.DataFrame()
    teams_matchs_data = []
    try:
        with engine.connect() as conn:
            query = sql_text("SELECT * FROM torneos_primera_arg.url_equipos")
            df_result = pd.read_sql_query(query, conn)
            df_teams = pd.concat([df_teams, df_result], ignore_index=True)
            df_teams_filtered = df_teams[(df_teams['year'].isin(yearr_list)) & (df_teams['code'].isin(cod_list))]
            df_teams_filtered['json_data'] = df_teams_filtered['json_data'].apply(json.loads)
            print("-----------------------------------json_data-------------------------------------------")
            for item in df_teams_filtered['json_data']:
                print(type(item))
                teams_matchs_data.append(item)  # Collect JSON data for all items
            return JSONResponse(content=teams_matchs_data, status_code=200)  # Return all JSON data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot find the request data: {str(e)}")