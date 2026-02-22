import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()

# Configuración de archivos estáticos y plantillas
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# La API_KEY se toma de las variables de entorno de Render
API_KEY = os.getenv("API_KEY")

def obtener_toda_la_info(ciudad):
    # 1. Obtener clima de OpenWeather
    url_w = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
    res_w = requests.get(url_w).json()

    if res_w.get("cod") != 200:
        return None

    # 2. Obtener datos del país de RestCountries
    cod_pais = res_w["sys"]["country"]
    url_c = f"https://restcountries.com/v3.1/alpha/{cod_pais}"
    res_c_data = requests.get(url_c).json()
    res_c = res_c_data[0]

    # 3. Organizar los 10 datos + Latitud y Longitud
    return {
        "city": res_w["name"],
        "country": res_c["name"]["common"],
        "flag": res_c["flags"]["png"],
        "region": res_c.get("region"),
        "population": res_c.get("population"),
        "latitude": res_w["coord"]["lat"],
        "longitude": res_w["coord"]["lon"],
        "weather_desc": res_w["weather"][0]["description"].capitalize(),
        "temperature": res_w["main"]["temp"],
        "feels_like": res_w["main"]["feels_like"],
        "humidity": res_w["main"]["humidity"],
        "pressure": res_w["main"]["pressure"],
        "wind_speed": res_w["wind"]["speed"],
        "wind_deg": res_w["wind"].get("deg"),
        "visibility": res_w.get("visibility", 0) / 1000,
        "clouds": res_w["clouds"]["all"],
        "temp_max": res_w["main"]["temp_max"],
        "temp_min": res_w["main"]["temp_min"],
        "sunrise": datetime.fromtimestamp(res_w["sys"]["sunrise"]).strftime('%H:%M'),
        "sunset": datetime.fromtimestamp(res_w["sys"]["sunset"]).strftime('%H:%M')
    }

@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/city/{nombre_ciudad}")
async def api_ciudad(nombre_ciudad: str):
    datos = obtener_toda_la_info(nombre_ciudad)
    return datos if datos else {"error": "Ciudad no encontrada"}