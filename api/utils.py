import requests
from bs4 import BeautifulSoup
import datetime
import streamlit as st
import os

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
    return results

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
    return best_players

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
    return df_table_positions

## para los EQUIPOS!!
def get_match_data(url):
  match_page = requests.get(url)
  match_content = match_page.content
  soup = BeautifulSoup(match_content, "html.parser")
  div_scores = soup.find('div', id='marcador')
  div_scores = [div_score for div_score in div_scores.find_all('div', class_='resultado')] if div_scores else []
  scores = []
  for div_scor in div_scores:
    sp = div_scor.text.strip()
    print("-----------------------------sp----------------------------------")
    print(sp)
    scores.append(sp)
  scores = "-".join(scores)
  print("-----------------------------scores----------------------------------")
  print(scores)
  ul_nombre_torneo = soup.find('ul', id='crumbs')
  li_nombre_torneo = [li for li in ul_nombre_torneo if ul_nombre_torneo and '\n' not in li] if ul_nombre_torneo else []
  nombre_torneo = [a for a in li_nombre_torneo[1].find('a')] if len(li_nombre_torneo)>0 else []
  all_spans = soup.find_all('span')
  list_goleadores_locales = []
  list_goleadores_visitantes = []
  list_amarillas_locales = []
  list_amarillas_visitantes = []
  for sp in all_spans:
    if 'left' in sp.get('class', []) and 'minutos' not in sp.get('class', []):
      goleadores_locales = [a.text for a in sp.find_all('a') if 'Gol de' in sp.find('small').text and a != ""]
      if len(goleadores_locales) > 0:
        list_goleadores_locales.append(goleadores_locales[0])
      amarillas_locales = [a.text for a in sp.find_all('a') if 'T. Amarilla' in sp.find('small').text and a != ""]
      if len(amarillas_locales) > 0:
        list_amarillas_locales.append(amarillas_locales[0])
    if 'right' in sp.get('class', []) and 'minutos' not in sp.get('class', []):
      goleadores_visitantes = [a.text for a in sp.find_all('a') if 'Gol de' in sp.find('small').text and a != ""]
      if len(goleadores_visitantes) > 0:
        list_goleadores_visitantes.append(goleadores_visitantes[0])
      amarillas_visitantes = [a.text for a in sp.find_all('a') if 'T. Amarilla' in sp.find('small').text and a != ""]
      if len(amarillas_visitantes) > 0:
        list_amarillas_visitantes.append(amarillas_visitantes[0])
  # list_goleadores_locales = {f"Gol {i+1}": goleador for i, goleador in enumerate(list_goleadores_locales)}
  # list_goleadores_visitantes = {f"Gol {i+1}": goleador for i, goleador in enumerate(list_goleadores_visitantes)}
  # list_amarillas_locales = {f"T. amarilla {i+1}": goleador for i, goleador in enumerate(list_amarillas_locales)}
  # list_amarillas_visitantes = {f"T. amarilla {i+1}": goleador for i, goleador in enumerate(list_amarillas_visitantes)}
  match_data = {
    'tournament': nombre_torneo[0] if len(nombre_torneo)>0 else [],
    'score': scores,
    'goles_local': list_goleadores_locales if len(list_goleadores_locales) > 0 else [],
    'goles_visitante': list_goleadores_visitantes if len(list_goleadores_visitantes) > 0 else [],
    'amarillas_local': list_amarillas_locales if len(list_amarillas_locales) > 0 else [],
    'amarillas_visitante': list_amarillas_visitantes if len(list_amarillas_visitantes) > 0 else []
  }
  # print(match_data)
  return match_data

## para los EQUIPOS!!
def get_team_data(url):
  page = requests.get(url)
  content = page.content
  soup = BeautifulSoup(content, "html.parser")
  partidos = soup.find_all(id='tablemarcador')
  matchs_data = []
  for partido in partidos:
    tr_partidos = partido.find_all('tr')
    for tr_partido in tr_partidos:
      td_fecha = tr_partido.find('td', class_='time')
      fecha = [fecha.text.strip() for fecha in td_fecha if td_fecha]
      td_status = tr_partido.find('td', class_='timer')
      status = [status.text.strip() for status in td_status.find('span') if td_status]
      td_team_home = tr_partido.find('td', class_='team-home')
      team_home_span = td_team_home.find('span') if td_team_home else None
      team_home_a = team_home_span.find('a') if team_home_span else None
      team_home = team_home_a.text.strip() if team_home_a else ''
      td_away_team = tr_partido.find('td', class_='team-away')
      team_away_span = td_away_team.find('span') if td_away_team else None
      team_away_a = team_away_span.find('a') if team_away_span else None
      team_away = team_away_a.text.strip() if team_away_a else ''
      td_link_partidos = tr_partido.find_all('td', class_='tdinfo')
      links = [link.find('a')['href'] for link in td_link_partidos if link.find('a')]
      match_data = get_match_data(links[0])
      print("----------------------------------------------------RETURN JSON DATA--------------------------------------------------------")
      combined_data = {
        'date': fecha[0],
        'status': status[0],
        'home_team': team_home,
        'away_team': team_away,
        'link': links[0],
        **match_data
      }
      print(combined_data)
      print("----------------------------------------------------------------------------------------------------------------------------")
      matchs_data.append(combined_data)
  print(matchs_data)
  return matchs_data