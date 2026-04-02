
import requests
import os
import random
from datetime import datetime

# CONFIG MASTER BRIEFING
TMDB_KEY = "14c15425ed275359fc0fc82fbbda1e62"
JSONBIN_KEY = "$2a$10$2FU4DfoZscB5BrItbrVx3ezRVN5ynuE1zH1Zy3X6IW5NP8p3pigwe"
BIN_ID = "69ce041936566621a870294e"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = "-1003835663170"

def enviar_promo(titulo, poster_url, es_estreno=True):
    tipo = "NUEVO ESTRENO DISPONIBLE" if es_estreno else "RECOMENDACION DEL DIA"
    caption = (
        f"{tipo}: {titulo}\n\n"
        f"SYNAPT NETWORK PRESENTA ELFILME.COM. ACCESO EXCLUSIVO A CARTELERA VIP. "
        f"STREAM THE FUTURE.\n\n"
        f"VISITA LA PLATAFORMA PARA VER ESTE CONTENIDO EN ALTA DEFINICION.\n\n"
        f"FUENTE: TMDB API\n"
        f"#elfilme #synaptnetwork #streaming #estrenos #premium\n\n"
        f"synapt.live | elfilme.com | synfm.online | inventario.rest | t.me/synaptliveofficial"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    requests.post(url, data={"chat_id": CHAT_ID, "photo": poster_url, "caption": caption})

def run():
    # Detectar día (0=Lunes, 1=Martes...)
    hoy = datetime.now().weekday()
    
    # 1. OBTENER DATOS ACTUALES (Siempre los necesitamos para la promo)
    headers = {"X-Master-Key": JSONBIN_KEY}
    res_get = requests.get(f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest", headers=headers)
    pelis_actuales = res_get.json()['record']

    if hoy == 0: # ES LUNES: ACTUALIZAR CATALOGO
        print("SINCRONIZANDO CARTELERA SEMANAL...")
        movies = []
        for p in range(1, 4):
            url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_KEY}&language=es-MX&page={p}&region=MX"
            data = requests.get(url).json()
            for m in data.get('results', []):
                if m.get('poster_path'):
                    movies.append({
                        "title": m['title'].upper(),
                        "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}",
                        "url_stream": f"https://vidsrc.me/embed/movie?tmdb={m['id']}&lang=es"
                    })
        # Guardar en JSONBin
        requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID}", json=movies, headers={"Content-Type": "application/json", "X-Master-Key": JSONBIN_KEY})
        enviar_promo(movies[0]['title'], movies[0]['poster'], es_estreno=True)
    else: # MARTES A DOMINGO: SOLO PROMO
        print("GENERANDO PROMO DIARIA...")
        peli_random = random.choice(pelis_actuales)
        enviar_promo(peli_random['title'], peli_random['poster'], es_estreno=False)

if __name__ == "__main__":
    run()
