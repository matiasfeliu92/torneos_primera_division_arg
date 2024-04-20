import pandas as pd
import sys
import os
sys.path.append('C:\\Users\\PC\\Documents\\Matias\\torneos_primera_division_arg')
from db import *
from utils import get_tournament_results, get_team_data

args = sys.argv
df_tournaments = pd.read_csv('../CSV/url_torneos.csv')
df_teams = pd.read_csv('../CSV/url_equipos.csv')

def post_teams_in_DB(anio):
    df_team = pd.DataFrame()
    selected_team = None
    teams_matchs = ''
    for index, row in df_teams.iterrows():
        url = row['url']
        code = row['code']
        name = row['nombre']
        if anio in url:
            print(url)
            teams_matchs = get_team_data(url)
            df_team = pd.concat([df_team, pd.DataFrame(teams_matchs)], ignore_index=True)
            print(df_team.shape)
            print(df_team.columns)
            df_team['code'] = code
            year = url[-4:]
            df_team['year'] = year
            df_team['team'] = name
            df_team.to_csv(f'../CSV/Club_{name}_{year}.csv')
            df_team.to_sql(f'Club_{name}_{year}', engine, if_exists='replace', schema='torneos_primera_arg', index=False)
            print(F"TABLE Club_{name}_{year} WAS SAVED SUCCESSFULY")

parametro = args[1]

if __name__ == '__main__':
    post_teams_in_DB(parametro)