import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import random

# CONFIGURACIÓN
JSONBIN_KEY = "$2a$10$2FU4DfoZscB5BrItbrVx3ezRVN5ynuE1zH1Zy3X6IW5NP8p3pigwe"
BIN_ID_NEWS = "69cc735aaaba882197b21a03"
TMDB_KEY = "14c15425ed275359fc0fc82fbbda1e62"
RSS_FEED_URL = "https://news.google.com/rss/search?q=cine+estrenos+netflix+marvel+dc&hl=es-419&gl=MX&ceid=MX:es-419"

# Imágenes de respaldo estilo "Netflix-core" para que el noticiero no se vea vacío
BACKDROP_RESERVAS = [
    "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1485846234645-a62644f84728?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1517604401157-538e966e6c4a?q=80&w=1000&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=1000&auto=format&fit=crop"
]

def get_real_news():
    print("📡 COSECHANDO NOTICIAS...")
    try:
        response = requests.get(RSS_FEED_URL)
        root = ET.fromstring(response.content)
        news_list = []
        for item in root.findall('./channel/item')[:12]:
            title = item.find('title').text.split(' - ')[0]
            
            # Asignamos una imagen aleatoria de alta calidad para que se vea premium
            img_noticia = random.choice(BACKDROP_RESERVAS)

            news_list.append({
                "title": title.upper(),
                "description": "Reporte de última hora desde Synapt News Network. stream the future.",
                "image": img_noticia, # Ahora sí tendrá imagen siempre
                "url": item.find('link').text,
                "source": item.find('source').text if item.find('source') is not None else "Synapt News",
                "publishedAt": item.find('pubDate').text
            })
        return news_list
    except: return []

def get_trending_movies():
    print("🎬 OBTENIENDO TRENDING MOVIES...")
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_KEY}&language=es-MX"
    try:
        res = requests.get(url).json()
        movies = []
        for m in res.get('results', [])[:10]:
            movies.append({
                "title": m.get('title'),
                "poster": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}",
                "backdrop": f"https://image.tmdb.org/t/p/original{m.get('backdrop_path')}",
                "rating": m.get('vote_average'),
                "releaseDate": m.get('release_date'),
                "overview": m.get('overview'),
                "tmdbUrl": f"https://www.themoviedb.org/movie/{m.get('id')}"
            })
        return movies
    except: return []

def run():
    noticias = get_real_news()
    tendencias = get_trending_movies()

    payload = {
        "updatedAt": datetime.now().isoformat(),
        "news": noticias,
        "movies": tendencias
    }

    headers = {"X-Master-Key": JSONBIN_KEY, "Content-Type": "application/json"}
    print(f"📤 ACTUALIZANDO ELFILME...")
    res = requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID_NEWS}", json=payload, headers=headers)
    
    if res.status_code == 200: print("✅ ÉXITO: NOTICIAS CON IMÁGENES Y TRENDING LISTO")
    else: print(f"❌ ERROR: {res.text}")

if __name__ == "__main__":
    run()
