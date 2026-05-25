import requests
import os
from datetime import datetime

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

def get_trending_movie():
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}&language=es-ES"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if data.get("results"):
            return data["results"][0]
        return None
    except Exception as e:
        print(f"Error TMDB: {e}")
        return None

def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=es-ES"
    try:
        return requests.get(url, timeout=15).json()
    except Exception as e:
        print(f"Error detalles: {e}")
        return {}

def already_in_notion(tmdb_id):
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    payload = {"filter": {"property": "TMDB_ID", "number": {"equals": tmdb_id}}, "page_size": 1}
    try:
        data = requests.post(url, json=payload, headers=headers, timeout=15).json()
        return len(data.get("results", [])) > 0
    except Exception as e:
        print(f"Error duplicado: {e}")
        return False

def generate_caption_with_groq(movie):
    prompt = f"Caption corto y emocionante en espanol con emojis para: {movie['title']} ({movie.get('release_date','')[:4]}). Sinopsis: {movie.get('overview','')[:300]}. Termina con llamado a la accion. Solo el caption."
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "max_tokens": 400, "temperature": 0.8}
    try:
        return requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=20).json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error Groq: {e}")
        return f"{movie['title']}
{movie.get('overview','')[:200]}"

def send_to_telegram(caption, image_url):
    payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "HTML"}
    if image_url:
        payload["photo"] = image_url
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto", data=payload, timeout=15)
        print("Telegram OK")
    except Exception as e:
        print(f"Error Telegram: {e}")

def save_to_notion(movie, details, caption):
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    genres = details.get("genres", [])
    genre_str = ", ".join(g["name"] for g in genres[:3]) if genres else ""
    rating_val = movie.get("vote_average") or details.get("vote_average")
    rating = round(float(rating_val), 1) if rating_val else None
    poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
    data = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": movie["title"]}}]},
            "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
            "Caption": {"rich_text": [{"text": {"content": caption}}]},
            "TMDB_ID": {"number": movie["id"]},
            "Poster": {"url": poster_url},
            "Rating": {"number": rating},
            "Genre": {"rich_text": [{"text": {"content": genre_str}}] if genre_str else []}
        }
    }
    try:
        requests.post("https://api.notion.com/v1/pages", json=data, headers=headers, timeout=15)
        print(f"Notion OK — Rating: {rating}, Genero: {genre_str}")
    except Exception as e:
        print(f"Error Notion: {e}")

def main():
    print("ElFilme Daily Post iniciando...")
    movie = get_trending_movie()
    if not movie:
        print("Sin pelicula trending")
        return
    print(f"Pelicula: {movie['title']} (ID: {movie['id']})")
    if already_in_notion(movie["id"]):
        print(f"Ya en Notion, omitiendo: {movie['title']}")
        return
    details = get_movie_details(movie["id"])
    caption = generate_caption_with_groq(movie)
    image_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
    send_to_telegram(caption, image_url)
    save_to_notion(movie, details, caption)
    print("Completado!")

if __name__ == "__main__":
    main()
