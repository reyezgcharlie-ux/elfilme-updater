import requests
import os
from datetime import datetime

# ============================================
# VARIABLES DE ENTORNO (Secrets de GitHub)
# ============================================
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")


def get_trending_movie():
    """Obtiene la película más trending del día desde TMDB"""
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}&language=es-ES"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if data.get("results"):
            return data["results"][0]  # La más popular del día
        return None
    except Exception as e:
        print(f"Error al obtener película de TMDB: {e}")
        return None


def generate_caption_with_groq(movie):
    """Genera un caption atractivo usando Groq (Llama 3)"""
    prompt = f"""Escribe un caption corto, atractivo y en español para Telegram/Instagram sobre esta película:

Título: {movie['title']}
Sinopsis: {movie.get('overview', 'Sin sinopsis disponible')}
Año: {movie.get('release_date', '????')[:4]}
Puntuación: {movie.get('vote_average', 'N/A')}

Hazlo emocionante, con emojis, máximo 5 líneas, y termina con un llamado a la acción (ej: ¿Ya la viste?).

Solo devuelve el texto del caption, nada más."""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.8
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error con Groq: {e}")
        return f"🎬 {movie['title']}\n\n{movie.get('overview', '')[:200]}..."


def send_to_telegram(caption, image_url):
    """Envía la publicación a Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption,
        "parse_mode": "HTML"
    }
    if image_url:
        payload["photo"] = image_url

    try:
        requests.post(url, data=payload, timeout=15)
        print("✅ Enviado a Telegram")
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")


def save_to_notion(movie, caption):
    """Guarda el registro en Notion"""
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "Title": {
                "title": [{"text": {"content": movie['title']}}]
            },
            "Date": {
                "date": {"start": datetime.now().strftime("%Y-%m-%d")}
            },
            "Caption": {
                "rich_text": [{"text": {"content": caption}}]
            },
            "TMDB_ID": {
                "number": movie['id']
            },
            "Poster": {
                "url": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}" if movie.get('poster_path') else None
            }
        }
    }

    try:
        requests.post(url, json=data, headers=headers, timeout=15)
        print("✅ Guardado en Notion")
    except Exception as e:
        print(f"Error guardando en Notion: {e}")


def main():
    print("🎬 Iniciando ElFilme Daily Post...")

    movie = get_trending_movie()
    if not movie:
        print("❌ No se pudo obtener película trending")
        return

    print(f"📽️ Película del día: {movie['title']}")

    caption = generate_caption_with_groq(movie)
    image_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None

    send_to_telegram(caption, image_url)
    save_to_notion(movie, caption)

    print("✅ Publicación completada con éxito!")


if __name__ == "__main__":
    main()