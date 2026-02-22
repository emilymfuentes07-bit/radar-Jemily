from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
from datetime import datetime
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Recuerda configurar esto en las variables de entorno de Render como API_KEY
API_KEY = os.getenv("API_KEY", "cac03bddd0d1aafbcc63779a34c47c53")

def obtener_toda_la_info(ciudad):
    url_w = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
    res_w = requests.get(url_w).json()
    
    if res_w.get("cod") != 200:
        return None

    c_code = res_w["sys"]["country"]
    res_c = requests.get(f"https://restcountries.com/v3.1/alpha/{c_code}").json()[0]

    # --- AJUSTE DE COHERENCIA HORARIA ---
    # Obtenemos el desplazamiento (timezone) en segundos de la ciudad
    offset = res_w.get("timezone", 0) 
    
    # Calculamos la hora local sumando el offset al tiempo UTC
    sunrise_local = datetime.utcfromtimestamp(res_w["sys"]["sunrise"] + offset).strftime('%H:%M')
    sunset_local = datetime.utcfromtimestamp(res_w["sys"]["sunset"] + offset).strftime('%H:%M')

    return {
        "city": res_w["name"],
        "region": res_c.get("region"),
        "country": res_c["name"]["common"],
        "latitude": res_w["coord"]["lat"],
        "longitude": res_w["coord"]["lon"],
        "population": res_c.get("population"),
        "currency": list(res_c.get("currencies", {}).keys())[0],
        "flag": res_c["flags"]["png"],
        "temperature": res_w["main"]["temp"],
        "weather_desc": res_w["weather"][0]["description"].capitalize(),
        "feels_like": res_w["main"]["feels_like"],
        "humidity": res_w["main"]["humidity"],
        "pressure": res_w["main"]["pressure"],
        "wind_speed": res_w["wind"]["speed"],
        "clouds": res_w["clouds"]["all"],
        "visibility": res_w.get("visibility", 0) / 1000,
        "temp_max": res_w["main"]["temp_max"],
        "temp_min": res_w["main"]["temp_min"],
        "sunrise": sunrise_local, # Hora local de la ciudad
        "sunset": sunset_local    # Hora local de la ciudad
    }

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/city/{ciudad}")
def buscar_ciudad(ciudad: str):
    data = obtener_toda_la_info(ciudad)
    if not data: raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    return data