import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

from db import db_connection

df_tournament_results = pd.DataFrame()
df_best_players = pd.DataFrame()
df_table_positions = pd.DataFrame()

database_url = os.getenv('DATABASE_URL') or st.secrets["DATABASE_URL"]

def get_tournament_results(url, torneo):
    global df_tournament_results
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    jornadas = soup.find_all(id='col-resultados')
    results = []
    for jornada in jornadas:
        nro_jornada = jornada.find(class_='titlebox').text
        tablaJornada = jornada.find('table')
        partidosJornada = tablaJornada.find_all('tr')
        for partido in partidosJornada:
            data = partido.find_all('td')
            if len(data) > 0:
                fecha_partido = data[0].text.strip()
                equipo_local = data[1].find('img').get('alt').strip()
                resultado = data[2].find('a').text.strip()
                equipo_visitante = data[3].find('img').get('alt').strip()
                try:
                    equipo_local_resultado = resultado.split('-')[0].strip()
                    equipo_visitante_resultado = resultado.split('-')[1].strip()
                except:
                    equipo_local_resultado = '-'
                    equipo_visitante_resultado = '-'
                results.append({
                    'nombre_torneo': torneo,
                    'nro_jornada': nro_jornada,
                    'fecha_partido': fecha_partido,
                    'equipo_local': equipo_local,
                    'resultado': resultado,
                    'equipo_visitante': equipo_visitante,
                    'equipo_local_resultado': equipo_local_resultado,
                    'equipo_visitante_resultado': equipo_visitante_resultado
                })
    df = pd.DataFrame(results)
    df_tournament_results = pd.concat([df_tournament_results, df], ignore_index=True)
    df_tournament_results.to_sql('tournament_results', db_connection(str(database_url)), if_exists='replace', index=False)
    df_tournament_results.to_csv('./CSV/tournament_results.csv')
    return df_tournament_results

def get_best_players(url, torneo):
    global df_best_players
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    goleadores = soup.find_all(id='informacion-goleadores')
    best_players = []
    for goleador in goleadores:
        jug_goleador = goleador.find('table')
        jug_goleador_data = jug_goleador.find_all('tr')
        for jugador in jug_goleador_data:
            data = jugador.find_all('td')
            if len(data) > 0:
                nombre = data[0].text.strip()
                goles = data[1].text.strip()
                equipo_element = data[2].find('a')
                equipo = equipo_element.get('title') if equipo_element is not None else None
                if nombre != 'Nombre' and goles != 'Goles' and equipo != 'Equipo':
                    best_players.append({
                        'nombre_torneo': torneo,
                        'nombre': nombre,
                        'cant_goles': goles,
                        'equipo': equipo,
                    })
    df = pd.DataFrame(best_players)
    df_best_players = pd.concat([df_best_players, df], ignore_index=True)
    df_best_players.to_sql('best_players', db_connection(str(database_url)), if_exists='replace', index=False)
    df_best_players.to_csv('./CSV/best_players.csv')
    return df_best_players

def get_positions_table(url, torneo):
    global df_table_positions
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    table_positions = []
    positions = soup.find_all(id='clasificacion')
    for position in positions:
        position_table = position.find('table')
        position_table_data = position_table.find_all('tr')
        for pos in position_table_data:
            data = pos.find_all('td')
            if len(data) > 0:
                equipo = data[0].text.strip()
                pj = data[1].text.strip()
                gf = data[2].text.strip()
                gc = data[3].text.strip()
                puntos = data[4].text.strip()
                if equipo != 'Equipo' and pj != 'PJ' and gf != 'GF' and gc != 'GC' and puntos != 'Puntos':
                    table_positions.append({
                        'nombre_torneo': torneo,
                        'equipo': equipo,
                        'PJ': pj,
                        'GF': gf,
                        'GC': gc,
                        'puntos': puntos
                    })
    df = pd.DataFrame(table_positions)
    df_table_positions = pd.concat([df_table_positions, df], ignore_index=True)
    df_table_positions.to_sql('table_positions', db_connection(str(database_url)), if_exists='replace', index=False)
    df_table_positions.to_csv('./CSV/table_positions.csv')
    return df_table_positions