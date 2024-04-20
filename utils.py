import json
import requests
from bs4 import BeautifulSoup
import datetime
import streamlit as st
import os

def get_tournament_results(url, tournament):
    global df_tournament_results
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    journeys = soup.find_all(id='col-resultados')
    results = []
    for journey in journeys:
        journey = journey.find(class_='titlebox').text
        journey_table = journey.find('table')
        journey_matchs = journey_table.find_all('tr')
        for match in journey_matchs:
            data = match.find_all('td')
            if len(data) > 0:
                date = data[0].text.strip()
                local_team = data[1].find('img').get('alt').strip()
                results = data[2].find('a').text.strip()
                away_team = data[3].find('img').get('alt').strip()
                try:
                    local_team_results = results.split('-')[0].strip()
                    away_team_results = results.split('-')[1].strip()
                except:
                    local_team_results = '-'
                    away_team_results = '-'
                results.append({
                    'nombre_torneo': tournament,
                    'journey': journey,
                    'date': date,
                    'local_team': local_team,
                    'resultado': results,
                    'away_team': away_team,
                    'local_team_results': local_team_results,
                    'away_team_results': away_team_results
                })
    return results

def get_best_players(url, tournament):
    global df_best_players
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    scorers = soup.find_all(id='informacion-goleadores')
    best_players = []
    for scorer in scorers:
        scoring_player = scorer.find('table')
        scoring_player_data = scoring_player.find_all('tr')
        for player in scoring_player_data:
            data = player.find_all('td')
            if len(data) > 0:
                name = data[0].text.strip()
                goals = data[1].text.strip()
                team_element = data[2].find('a')
                team = team_element.get('title') if team_element is not None else None
                if name != 'Nombre' and goals != 'Goles' and team != 'Equipo':
                    best_players.append({
                        'tournament': tournament,
                        'name': name,
                        'goals': goals,
                        'team': team,
                    })
    return best_players

def get_positions_table(url, tournament):
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
                team = data[0].text.strip()
                pj = data[1].text.strip()
                gf = data[2].text.strip()
                gc = data[3].text.strip()
                points = data[4].text.strip()
                if team != 'Equipo' and pj != 'PJ' and gf != 'GF' and gc != 'GC' and points != 'Puntos':
                    table_positions.append({
                        'tournament': tournament,
                        'team': team,
                        'PJ': pj,
                        'GF': gf,
                        'GC': gc,
                        'points': points
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
    # print("-----------------------------sp----------------------------------")
    # print(sp)
    scores.append(sp)
  scores = "-".join(scores)
  # print("-----------------------------scores----------------------------------")
  # print(scores)
  ul_tournament_name = soup.find('ul', id='crumbs')
  li_tournament_name = [li for li in ul_tournament_name if ul_tournament_name and '\n' not in li] if ul_tournament_name else []
  tournament_name = [a for a in li_tournament_name[1].find('a')] if len(li_tournament_name)>0 else []
  all_spans = soup.find_all('span')
  local_scorers_list = []
  away_scorers_list = []
  local_yellow_card_list = []
  list_away_yellow_cards = []
  statistic_list = None
  statistic_dict = {}
  for sp in all_spans:
    if 'left' in sp.get('class', []) and 'minutos' not in sp.get('class', []):
      local_scorers = [a.text for a in sp.find_all('a') if 'Gol de' in sp.find('small').text and a != ""]
      if len(local_scorers) > 0:
        local_scorers_list.append(local_scorers[0])
      local_yellow_cards = [a.text for a in sp.find_all('a') if 'T. Amarilla' in sp.find('small').text and a != ""]
      if len(local_yellow_cards) > 0:
        local_yellow_card_list.append(local_yellow_cards[0])
    if 'right' in sp.get('class', []) and 'minutos' not in sp.get('class', []):
      away_scorers = [a.text for a in sp.find_all('a') if 'Gol de' in sp.find('small').text and a != ""]
      if len(away_scorers) > 0:
        away_scorers_list.append(away_scorers[0])
      away_yellow_cards = [a.text for a in sp.find_all('a') if 'T. Amarilla' in sp.find('small').text and a != ""]
      if len(away_yellow_cards) > 0:
        list_away_yellow_cards.append(away_yellow_cards[0])
  matchs_statistics = []
  div_statistic_table = soup.select('div.contentitem table')
  # print("----------------------------------div_statistic_table-----------------------------------------")
  # print(div_statistic_table)
  statistic_table = [table.find('tbody') for table in div_statistic_table] if div_statistic_table else []
  tr_elements = [tr for table in statistic_table for tr in table.find_all('tr')]
  # print("LENGHT TRS: ", len(tr_elements))
  for tr in tr_elements:
    # print("-------------------------CADA TR-------------------------------")
    # print(tr.find_all('td')[1].find('h6').text.strip())
    if tr.find_all('td')[1].find('h6').text.strip() == 'Posesión del balón':
      statistic_dict['local_ball_position'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_ball_position'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Goles':
      statistic_dict['local_goals'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_goals'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Tiros a puerta':
      statistic_dict['local_kicks_to_goals'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_kicks_to_goals'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Tiros fuera':
      statistic_dict['local_outside_kicks'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_outside_kicks'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Total tiros':
      statistic_dict['local_total_kicks'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_total_kicks'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Paradas del portero':
      statistic_dict['local_shortcuts'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_shortcuts'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Saques de esquina':
      statistic_dict['local_corner_kicks'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_corner_kicks'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Fueras de juego':
      statistic_dict['local_offside'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_offside'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Tarjetas Rojas':
      statistic_dict['local_red_cards'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_red_cards'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Asistencias':
      statistic_dict['local_assists'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_assists'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Tiros al palo':
      statistic_dict['local_crossbar_kicks'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_crossbar_kicks'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Lesiones':
      statistic_dict['local_lesions'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_lesions'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Sustituciones':
      statistic_dict['local_substitutions'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_substitutions'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Faltas':
      statistic_dict['local_faults'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_faults'] = tr.find_all('td')[2].text.strip()
    elif tr.find_all('td')[1].find('h6').text.strip() == 'Penalti cometido':
      statistic_dict['local_commited_penalties'] = tr.find_all('td')[0].text.strip()
      statistic_dict['away_commited_penalties'] = tr.find_all('td')[2].text.strip()
  # print("-------------------------statistic_dict-------------------------------")
  # print(statistic_dict)
  match_data = {
    'tournament': tournament_name[0] if len(tournament_name)>0 else '',
    'score': scores,
    'local_scorers': ', '.join(local_scorers_list) if len(local_scorers_list) > 0 else '',
    'away_scorers': ', '.join(away_scorers_list) if len(away_scorers_list) > 0 else '',
    'local_yellow_cards': ', '.join(local_yellow_card_list) if len(local_yellow_card_list) > 0 else '',
    'away_yellow_cards': ', '.join(list_away_yellow_cards) if len(list_away_yellow_cards) > 0 else '',
    'match_statistics': json.dumps(statistic_dict)
  }
  # print(match_data)
  return match_data

## para los EQUIPOS!!
def get_team_data(url):
  page = requests.get(url)
  content = page.content
  soup = BeautifulSoup(content, "html.parser")
  matchs = soup.find_all(id='tablemarcador')
  matchs_data = []
  for match in matchs:
    matchs_tr = match.find_all('tr')
    for match_tr in matchs_tr:
      date_td = match_tr.find('td', class_='time')
      date = [date.text.strip() for date in date_td if date_td]
      td_status = match_tr.find('td', class_='timer')
      status = [status.text.strip() for status in td_status.find('span') if td_status]
      td_team_home = match_tr.find('td', class_='team-home')
      team_home_span = td_team_home.find('span') if td_team_home else None
      team_home_a = team_home_span.find('a') if team_home_span else None
      team_home = team_home_a.text.strip() if team_home_a else ''
      td_away_team = match_tr.find('td', class_='team-away')
      team_away_span = td_away_team.find('span') if td_away_team else None
      team_away_a = team_away_span.find('a') if team_away_span else None
      team_away = team_away_a.text.strip() if team_away_a else ''
      matchs_links_td = match_tr.find_all('td', class_='tdinfo')
      links = [link.find('a')['href'] for link in matchs_links_td if link.find('a')]
      match_data = get_match_data(links[0])
      combined_data = {
        'date': date[0],
        'status': status[0],
        'home_team': team_home,
        'away_team': team_away,
        'link': links[0],
        **match_data
      }
      matchs_data.append(combined_data)
  return matchs_data