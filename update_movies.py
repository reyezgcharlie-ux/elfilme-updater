import requests
import os

TMDB_KEY = os.getenv('TMDB_KEY')
JSONBIN_KEY = os.getenv('JSONBIN_KEY')
BIN_ID = "69ce041936566621a870294e"

def run():
    movies = []
    # Pedimos 3 páginas para tener variedad
    for p in range(1, 4):
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_KEY}&language=es-MX&page={p}&region=MX"
        data = requests.get(url).json()
        
        for m in data.get('results', []):
            if m.get('poster_path'):
                # Lógica de Géneros de TMDB
                g_id = m['genre_ids'][0] if m.get('genre_ids') else 0
                category = "ESTRENOS" # Default
                if g_id in [28, 12]: category = "ACCIÓN"
                elif g_id in [27]: category = "TERROR"
                elif g_id in [16, 10751]: category = "ANIMACIÓN"
                elif g_id in [878]: category = "CIENCIA FICCIÓN"

                movies.append({
                    "title": m['title'].upper(),
                    "year": m['release_date'][:4] if m.get('release_date') else "2026",
                    "category": category, # <--- ESTO ES LO NUEVO
                    "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}",
                    "url_stream": f"https://vidsrc.me/embed/movie?tmdb={m['id']}&lang=es"
                })

    headers = {"Content-Type": "application/json", "X-Master-Key": JSONBIN_KEY}
    res = requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID}", json=movies, headers=headers)
    print("Sincronización con Categorías Exitosa" if res.status_code == 200 else "Error")

if __name__ == "__main__":
    run()
