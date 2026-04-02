import requests
import os

# Configuración desde GitHub Secrets
TMDB_KEY = os.getenv('TMDB_KEY')
JSONBIN_KEY = os.getenv('JSONBIN_KEY')
BIN_ID = "69ce041936566621a870294e"

def run():
    movies = []
    # Buscamos 3 páginas de estrenos (60 películas aprox)
    for p in range(1, 4):
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_KEY}&language=es-MX&page={p}&region=MX"
        data = requests.get(url).json()
        for m in data.get('results', []):
            if m.get('poster_path'):
                movies.append({
                    "title": m['title'].upper(),
                    "year": m['release_date'][:4] if m.get('release_date') else "2026",
                    "quality": "HD-LATINO",
                    "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}",
                    "url_stream": f"https://vidsrc.icu/embed/movie/{m['id']}"
                })

    # Subida automática a JSONBin
    headers = {"Content-Type": "application/json", "X-Master-Key": JSONBIN_KEY}
    res = requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID}", json=movies, headers=headers)
    print("Sincronización Exitosa" if res.status_code == 200 else f"Error: {res.text}")

if __name__ == "__main__":
    run()
