from fastapi import FastAPI,HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import sys
import json
sys.path.append('C:\\Users\\PC\\Documents\\Matias\\torneos_primera_division_arg')
from db import *

app = FastAPI()
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

@app.get("/index")
def read_root():
    return {"Hello": "World"}

@app.get("/tournaments")
def get_tournaments():
    df_tournaments = pd.DataFrame()
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM torneos_primera_arg.url_torneos")
            df_result = pd.read_sql_query(query, conn)
            df_tournaments = pd.concat([df_tournaments, df_result], ignore_index=True)
            tournaments = df_tournaments.to_dict(orient='records')
            return JSONResponse(content=tournaments, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot find the request data: {str(e)}")
    
@app.get("/teams")
def get_teams():
    df_teams = pd.DataFrame()
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM torneos_primera_arg.url_equipos")
            df_result = pd.read_sql_query(query, conn)
            df_teams = pd.concat([df_teams, df_result], ignore_index=True)
            teams = df_teams.to_dict(orient='records')
            return JSONResponse(content=teams, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot find the request data: {str(e)}")

# @app.post("/results")
# def post_results_in_DB(anio: str):
#     results_list = []
#     for index, row in df_tournaments.iterrows():
#         url = row['url']
#         nombre = row['nombre']
#         if anio in url:
#             results = get_tournament_results(url, nombre)
#             print(results)
#             results_list.append(results)
#     return results_list

@app.post("/teams")
def post_teams(yearr: str, cod: str):
    yearr = yearr.split(',')
    cod = cod.split(',')
    print(yearr)
    print(cod)
    df_teams_url = pd.DataFrame()
    df_teams_data = pd.DataFrame()
    try:
        with engine.connect() as conn:
            teams_urls_query = text("SELECT * FROM torneos_primera_arg.url_equipos")
            df_result = pd.read_sql_query(teams_urls_query, conn)
            df_teams_url = pd.concat([df_teams_url, df_result], ignore_index=True)
            df_teams_url_filtered = df_teams_url[ (df_teams_url.año.isin(yearr)) & (df_teams_url.code.isin(cod)) ]
            print(df_teams_url_filtered)
            for index, row in df_teams_url_filtered.iterrows():
                year = row['año']
                code = row['code']
                name = row['nombre']
                table_name = f'"Club_{name}_{year}"'
                print(table_name)
                team_table_query = text(f"SELECT * FROM torneos_primera_arg.{table_name}")
                df_team_table_query = pd.read_sql(team_table_query, conn)
                print(df_team_table_query)
                df_teams_data = pd.concat([df_teams_data, df_team_table_query])
            print(df_teams_data['team'].unique())
            print(df_teams_data['año'].unique())
            teams_data = df_teams_data.to_dict(orient='records')
        return JSONResponse(content={'teams_data': teams_data}, status_code=200)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        return JSONResponse(content={'error_message':error_message}, status_code=500)