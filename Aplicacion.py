from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # IMPORTANTE
import requests

app = FastAPI()

# Configuración de seguridad para que otros dispositivos entren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# REEMPLAZA ESTO CON TU CLAVE DE OPENWEATHER
API_KEY = "cac03bddd0d1aafbcc63779a34c47c53"

def obtener_toda_la_info(ciudad):
    url_w = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
    res_w = requests.get(url_w).json()
    
    if res_w.get("cod") != 200:
        return None

    c_code = res_w["sys"]["country"]
    res_c = requests.get(f"https://restcountries.com/v3.1/alpha/{c_code}").json()[0]

    return {
        "city": res_w["name"],
        "region": res_c.get("region"),
        "country": res_c["name"]["common"],
        "country_code": c_code,
        "latitude": res_w["coord"]["lat"],
        "longitude": res_w["coord"]["lon"],
        "population": res_c.get("population"),
        "currency": list(res_c.get("currencies", {}).keys())[0],
        "flag": res_c["flags"]["png"],
        "temperature": res_w["main"]["temp"],
        "feels_like": res_w["main"]["feels_like"],
        "humidity": res_w["main"]["humidity"],
        "weather_main": res_w["weather"][0]["main"],
        "weather_desc": res_w["weather"][0]["description"].capitalize(),
        "weather_icon": res_w["weather"][0]["icon"]
    }

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/city/{ciudad}")
def buscar_ciudad(ciudad: str):
    data = obtener_toda_la_info(ciudad)
    if not data: raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    return data