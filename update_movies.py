import requests
import os
import random
from datetime import datetime

# CONFIGURACIÓN MASTER BRIEFING
TMDB_KEY = "14c15425ed275359fc0fc82fbbda1e62"
JSONBIN_KEY = "$2a$10$2FU4DfoZscB5BrItbrVx3ezRVN5ynuE1zH1Zy3X6IW5NP8p3pigwe"
BIN_ID = "69ce041936566621a870294e"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = "-1003835663170"

def enviar_promo_editorial(titulo, poster_url, es_estreno=True):
    tipo = "NUEVO ESTRENO DISPONIBLE" if es_estreno else "RECOMENDACION DEL DIA"
    caption = (
        f"{tipo}: {titulo}\n\n"
        f"SYNAPT NETWORK PRESENTA ELFILME.COM. ACCESO EXCLUSIVO A CARTELERA VIP "
        f"ACTUALIZADA EN TIEMPO REAL. STREAM THE FUTURE.\n\n"
        f"VISITA LA PLATAFORMA PARA VER ESTE CONTENIDO EN ALTA DEFINICION.\n\n"
        f"FUENTE: TMDB API\n"
        f"#elfilme #synaptnetwork #streaming #estrenos #premium\n\n"
        f"synapt.live | elfilme.com | synfm.online | inventario.rest | t.me/synaptliveofficial"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    requests.post(url, data={"chat_id": CHAT_ID, "photo": poster_url, "caption": caption})

def generar_sitemap(movies):
    inicio = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    cuerpo = ""
    for m in movies:
        url_peli = f"https://elfilme.com/estrenos.html?title={m['title'].replace(' ', '+')}"
        cuerpo += f"  <url>\n    <loc>{url_peli}</loc>\n    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>\n  </url>\n"
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(inicio + cuerpo + "</urlset>")

def run():
    hoy = datetime.now().weekday()
    # 1. SIEMPRE OBTENER DATOS ACTUALES
    headers_get = {"X-Master-Key": JSONBIN_KEY}
    res_get = requests.get(f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest", headers=headers_get)
    pelis_actuales = res_get.json()['record']

    if hoy == 0: # LUNES: ACTUALIZACION TOTAL
        print("EJECUTANDO ACTUALIZACION SEMANAL SYNAPT...")
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
        # Guardar en JSONBin y generar Sitemap
        requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID}", json=movies, headers={"Content-Type": "application/json", "X-Master-Key": JSONBIN_KEY})
        generar_sitemap(movies)
        enviar_promo_editorial(movies[0]['title'], movies[0]['poster'], es_estreno=True)
    else: # RESTO DE LA SEMANA: SOLO MARKETING
        print("EJECUTANDO MARKETING DIARIO...")
        peli_promo = random.choice(pelis_actuales)
        enviar_promo_editorial(peli_promo['title'], peli_promo['poster'], es_estreno=False)

if __name__ == "__main__":
    run()
