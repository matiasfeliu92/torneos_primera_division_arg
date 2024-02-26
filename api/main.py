from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
from utils import get_tournament_results, get_team_data

app = FastAPI()

df_torneos = pd.read_csv('./csv/url_torneos.csv')
df_equipos = pd.read_csv('./csv/url_equipos.csv')

@app.get("/index")
def read_root():
    return {"Hello": "World"}

@app.get("/torneos")
def get_torneos():
    torneos = df_torneos.to_dict(orient='records')
    print(torneos)
    return JSONResponse(content=torneos)

@app.get("/equipos")
def get_torneos():
    equipos = df_equipos.to_dict(orient='records')
    print(equipos)
    return JSONResponse(content=equipos)

@app.post("/results")
def post_results(anio: str):
    results = None
    for index, row in df_torneos.iterrows():
        url = row['url']
        nombre = row['nombre']
        if anio in url:
            results = get_tournament_results(url, nombre)
            print(results)
            return results
            # print({'url_torneo': url, 'nombre_torneo': nombre})
            # return {'url_torneo': url, 'nombre_torneo': nombre}
        
@app.post("/teams")
def post_teams(anio: str, cod: str):
    teams_matchs_list = []
    for index, row in df_equipos.iterrows():
        url = row['url']
        code = row['code']
        if anio in url and cod == code:
            print(url)
            teams_matchs = get_team_data(url)
            print(teams_matchs)
            teams_matchs_list.append(teams_matchs)
            # Puedes agregar más lógica aquí si es necesario
    return teams_matchs_list