import os
import pandas as pd
from pandas.api.types import (is_numeric_dtype)
import numpy as np
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from sqlalchemy import text, engine, exc
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from db import db_connection
from utils import get_tournament_results, get_best_players, get_positions_table

df_url_torneos = pd.read_csv('./CSV/url_torneos.csv')
df_tournament_results = None
df_best_players = None
df_table_positions = None

st.set_page_config(layout="wide")

connection=None
with st.spinner('Loading dashboard, please wait...'):
    if not st.button('Update data'):
        connection = db_connection(str(os.getenv('DATABASE_URL'))).connect()
        try:
            if connection is not None:
                df_tournament_results = pd.read_sql('SELECT * FROM "public"."tournament_results"', con=db_connection(str(os.getenv('DATABASE_URL'))))
                df_best_players = pd.read_sql('SELECT * FROM "public"."best_players"', con=db_connection(str(os.getenv('DATABASE_URL'))))
                df_table_positions = pd.read_sql('SELECT * FROM "public"."table_positions"', con=db_connection(str(os.getenv('DATABASE_URL'))))
        except exc.SQLAlchemyError as e:
            print("Error al conectar a la base de datos:", e)
            df_tournament_results = pd.read_csv('/CSV/tournament_results.csv')
            df_best_players = pd.read_csv('/CSV/best_players.csv')
            df_table_positions = pd.read_csv('/CSV/table_positions.csv')
        finally:
            if connection is not None:
                connection.close()
    else:
        for index, row in df_url_torneos.iterrows():
            url = row['url']
            torneo = row['nombre']
            df_tournament_results = get_tournament_results(url, torneo)
            df_best_players = get_best_players(url, torneo)
            df_table_positions = get_positions_table(url, torneo)

st.spinner('')

st.title('Torneos de primera division del futbol argentino')

# st.dataframe(df_tournament_results.iloc[0:10])
# st.dataframe(df_best_players.iloc[0:10])
# st.dataframe(df_table_positions.iloc[0:10])

select_one_option = st.selectbox('Selecciona una opcion', ['Ninguna', 'Resultados de partidos', 'Los mejores jugadores', 'Posiciones'])

if select_one_option == 'Resultados de partidos':
    st.write('Resultados de partidos')
elif select_one_option == 'Los mejores jugadores':
    st.write('Los mejores jugadores')
elif select_one_option == 'Posiciones':
    st.write('Posiciones')
    for col in ['PJ', 'GF', 'GC', 'puntos']:
        df_table_positions[col] = df_table_positions[col].astype('int64')
    select_tournaments = st.multiselect('Selecciona un torneo', [torneo for torneo in df_table_positions['nombre_torneo'].unique()])
    torneos_unicos = sorted(select_tournaments, reverse=True)
    select_graph_type = st.selectbox('selecciona el grafico que quieras', ['bar_chart', 'line_chart', 'scatter_chart', 'pie_chart', 'dataframe'])
    print(select_tournaments)
    if len(select_tournaments) >= 1:
        torneos_unicos = select_tournaments if len(select_tournaments) == 1 else df_table_positions['nombre_torneo'].unique()

        num_columns = 2 if len(torneos_unicos) > 1 else 1
        columns = st.columns(num_columns)

        for i, torneo in enumerate(select_tournaments):
            data = df_table_positions[df_table_positions['nombre_torneo'] == torneo].sort_values('puntos', ascending=False)

            if select_graph_type == 'bar_chart':
                fig = px.bar(data, x='equipo', y='puntos', title=torneo, color='equipo', labels={'puntos': 'Puntos'})

                with columns[i % num_columns]:
                    st.plotly_chart(fig, use_container_width=True)
            elif select_graph_type == 'line_chart':
                fig = px.line(data, x='equipo', y='puntos', title=torneo, color='equipo', labels={'puntos': 'Puntos'})

                with columns[i % num_columns]:
                    st.plotly_chart(fig, use_container_width=True)
            elif select_graph_type == 'scatter_chart':
                fig = px.scatter(data, x='equipo', y='puntos', title=torneo, color='equipo', labels={'puntos': 'Puntos'})

                with columns[i % num_columns]:
                    st.plotly_chart(fig, use_container_width=True)
            elif select_graph_type == 'pie_chart':
                fig = px.pie(data, names='equipo', values='puntos', title=torneo, color='equipo', labels={'puntos': 'Puntos'})

                with columns[i % num_columns]:
                    st.plotly_chart(fig, use_container_width=True)
            elif select_graph_type == 'dataframe':
                with columns[i % num_columns]:
                    st.dataframe(data.iloc[0:10])


