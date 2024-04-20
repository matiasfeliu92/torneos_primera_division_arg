import pandas as pd
import sys
import os
sys.path.append('C:\\Users\\PC\\Documents\\Matias\\torneos_primera_division_arg')
from db import *

df_tournaments = pd.read_csv('../CSV/url_torneos.csv')
df_teams = pd.read_csv('../CSV/url_equipos.csv')
df_teams['year'] = df_teams['url'].str[-4:]
for col in df_teams.columns:
    if 'Unnamed' in col:
        df_teams.drop(col, axis=1, inplace=True)
df_teams.to_csv('../CSV/url_equipos.csv', index=False)
df_teams.to_sql('url_equipos', engine, if_exists='replace', schema='torneos_primera_arg', index=False)
print('TABLE url_equipos SAVED')
df_teams.to_csv('../CSV/url_torneos.csv', index=False)
df_tournaments.to_sql('url_torneos', engine, if_exists='replace', schema='torneos_primera_arg', index=False)
print('TABLE url_torneos SAVED')
