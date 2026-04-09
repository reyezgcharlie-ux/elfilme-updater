import requests
import os
import random
from datetime import datetime

# CONFIGURACIÓN MASTER - SYNAPT NETWORK
TMDB_KEY = "14c15425ed275359fc0fc82fbbda1e62"
JSONBIN_KEY = "$2a$10$2FU4DfoZscB5BrItbrVx3ezRVN5ynuE1zH1Zy3X6IW5NP8p3pigwe"
BIN_ID = "69ce041936566621a870294e"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = "-1003835663170"

def enviar_promo_editorial(titulo, poster_url, es_estreno=True):
    tipo = "🔥 NUEVO ESTRENO DISPONIBLE" if es_estreno else "✨ RECOMENDACIÓN DEL DÍA"
    caption = (
        f"{tipo}: {titulo}\n\n"
        f"SYNAPT NETWORK PRESENTA ELFILME.COM.\n"
        f"ACCESO EXCLUSIVO A CARTELERA VIP ACTUALIZADA EN TIEMPO REAL.\n"
        f"STREAM THE FUTURE.\n\n"
        f"🔗 Visita elfilme.com para ver este contenido en HD.\n\n"
        f"FUENTE: TMDB API\n"
        f"#elfilme #synaptnetwork #streaming #estrenos #premium\n\n"
        f"synapt.live | elfilme.com | synfm.online | t.me/synaptliveofficial"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "photo": poster_url, "caption": caption})
        print(f"✅ PROMO ENVIADA: {titulo}")
    except:
        print("⚠️ ERROR EN TELEGRAM PROMO")

def generar_sitemap(movies):
    inicio = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    cuerpo = ""
    for m in movies:
        url_peli = f"https://elfilme.com/estrenos.html?title={m['title'].replace(' ', '+')}"
        cuerpo += f"  <url>\n    <loc>{url_peli}</loc>\n    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>\n  </url>\n"
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(inicio + cuerpo + "</urlset>")
    print("✅ SITEMAP GENERADO LOCALMENTE")

def run():
    hoy = datetime.now().weekday() # 0=Lunes, 2=Miércoles
    headers = {"X-Master-Key": JSONBIN_KEY, "Content-Type": "application/json"}
    
    # 1. SIEMPRE OBTENER DATOS ACTUALES
    try:
        res_get = requests.get(f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest", headers=headers)
        pelis_actuales = res_get.json().get('record', [])
    except:
        pelis_actuales = []
        print("⚠️ NO SE PUDO LEER JSONBIN")

    datos_finales = pelis_actuales

    # 2. LÓGICA POR DÍA
    if hoy == 0: # LUNES: ACTUALIZACIÓN TOTAL
        print("🚀 EJECUTANDO ACTUALIZACIÓN SEMANAL SYNAPT...")
        movies_nuevas = []
        for p in range(1, 4):
            url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_KEY}&language=es-MX&page={p}&region=MX"
            data = requests.get(url).json()
            for m in data.get('results', []):
                if m.get('poster_path'):
                    video_url = f"https://vidsrc.me/embed/movie?tmdb={m['id']}&lang=es"
                    movies_nuevas.append({
                        "title": m['title'].upper(),
                        "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}",
                        "url_stream": video_url,
                        "link": video_url
                    })
        if movies_nuevas:
            datos_finales = movies_nuevas
            enviar_promo_editorial(datos_finales[0]['title'], datos_finales[0]['poster'], es_estreno=True)
    
    else: # RESTO DE LA SEMANA: MARKETING DIARIO
        print("📱 EJECUTANDO MARKETING DIARIO...")
        if pelis_actuales:
            peli_promo = random.choice(pelis_actuales)
            enviar_promo_editorial(peli_promo['title'], peli_promo['poster'], es_estreno=False)

    # 3. GUARDADO OBLIGATORIO (FUERA DEL IF)
    # Esto garantiza que el JSON y el Sitemap se actualicen aunque sea miércoles
    if datos_finales:
        res_put = requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID}", json=datos_finales, headers=headers)
        if res_put.status_code == 200:
            print("✅ JSONBIN SINCRONIZADO")
        generar_sitemap(datos_finales)

if __name__ == "__main__":
    run()
