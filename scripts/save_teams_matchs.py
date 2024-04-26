import json
import pandas as pd
import psycopg2
from sqlalchemy import Column, MetaData, Table, create_engine, exc, text as sql_text, update
from decouple import config
from dotenv import load_dotenv
import sys
import os
sys.path.append('C:\\Users\\PC\\Documents\\Matias\\torneos_primera_division_arg')
from utils import get_tournament_results, get_team_data

load_dotenv()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)
print(engine.url)

# metadata = MetaData()
# metadata.reflect(bind=engine)

args = sys.argv
df_teams = pd.read_sql('SELECT * FROM "torneos_primera_arg"."url_equipos"', engine)

# def post_teams_in_DB(anio):
#     print(type(anio))
#     print(anio)
#     df_team = pd.DataFrame()
#     selected_team = None
#     teams_matchs = ''
#     for index, row in df_teams.iterrows():
#         url = row['url']
#         code = row['code']
#         name = row['nombre']
#         if anio in url:
#             print(url)
#             teams_matchs = get_team_data(url)
#             print(teams_matchs)
#             my_table = Table('url_equipos', metadata, autoload_with=engine, schema='torneos_primera_arg')
#             print("-----------------------------TABLA-------------------------------------")
#             ##json.dumps(teams_matchs, ensure_ascii=False)
#             print(my_table)
#             stmt = update(my_table).where(my_table.c.year == anio.strip()).values(json_data=json.dumps(teams_matchs, ensure_ascii=False))
#             print(stmt)
#             with engine.connect() as conn:
#                 conn.execute(stmt)
#             print("TABLE UPDATED SUCCESFULLY")
#             df_team = pd.concat([df_team, pd.DataFrame(teams_matchs)], ignore_index=True)
#             print(df_team.shape)
#             print(df_team.columns)
#             df_team['code'] = code
#             year = url[-4:]
#             df_team['year'] = year
#             df_team['team'] = name
#             df_teams.to_sql("url_equipos", engine, if_exists='replace', schema='torneos_primera_arg', index=False)
#             df_team.to_csv(f'../CSV/Club_{name}_{year}.csv')
#             df_team.to_sql(f'Club_{name}_{year}', engine, if_exists='replace', schema='torneos_primera_arg', index=False)
#             print(F"TABLE Club_{name}_{year} WAS SAVED SUCCESSFULY")

def post_teams_in_DB(anio):
    print(type(anio))
    print(anio)
    teams_matchs = ''
    df_teams_filtered = df_teams[df_teams.year == int(anio)]
    print(df_teams_filtered)
    for index, row in df_teams_filtered.iterrows():
        url = row['url']
        print(url)
        teams_matchs = get_team_data(url)
        print(teams_matchs)
        df_teams_filtered.at[index, 'json_data'] = json.dumps(teams_matchs, ensure_ascii=False)
        print(f"---------------------------------df_teams_filtered UPDATED by {url}--------------------------------------------")    
        print(df_teams_filtered)
    print("---------------------------------df_teams_filtered UPDATED--------------------------------------------")    
    print(df_teams_filtered)
    df_teams_1 = df_teams[df_teams.year != int(anio)]
    df_teams_final = pd.concat([df_teams_filtered, df_teams_1], ignore_index=True)
    df_teams_final.to_sql("url_equipos", engine, if_exists='replace', schema='torneos_primera_arg', index=False)
parametro = args[1]

if __name__ == '__main__':
    post_teams_in_DB(parametro)