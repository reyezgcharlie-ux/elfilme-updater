import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os

# CONFIGURACIÓN SYNAPT NEWS
JSONBIN_KEY = "$2a$10$2FU4DfoZscB5BrItbrVx3ezRVN5ynuE1zH1Zy3X6IW5NP8p3pigwe"
BIN_ID_NEWS = "69cc735aaaba882197b21a03"
# Feed de Google News para Cine en Español
RSS_FEED_URL = "https://news.google.com/rss/search?q=cine+estrenos+netflix+marvel+dc&hl=es-419&gl=MX&ceid=MX:es-419"

def get_real_news():
    print("📡 COSECHANDO NOTICIAS DESDE GOOGLE NEWS...")
    try:
        response = requests.get(RSS_FEED_URL)
        root = ET.fromstring(response.content)
        news_list = []
        
        # Tomamos las primeras 12 noticias
        for item in root.findall('./channel/item')[:12]:
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            source = item.find('source').text if item.find('source') is not None else "Cine News"
            
            # Limpiamos el título (Google suele poner "Título - Fuente")
            clean_title = title.split(' - ')[0]

            news_list.append({
                "title": clean_title.upper(),
                "description": f"Últimas novedades sobre el mundo del cine y el streaming. Más info en la fuente original.",
                "image": "https://elfilme.com/copilot_image_1772812453252.jpeg", # Imagen por defecto de Synapt
                "url": link,
                "source": source,
                "publishedAt": pub_date
            })
        return news_list
    except Exception as e:
        print(f"⚠️ Error al obtener noticias: {e}")
        return []

def run():
    # 1. Obtener las noticias frescas
    noticias = get_real_news()
    
    if not noticias:
        print("❌ No se pudieron recolectar noticias hoy.")
        return

    # 2. Preparar el payload para el Cloudflare Worker de elFilme
    payload = {
        "updatedAt": datetime.now().isoformat(),
        "news": noticias,
        "movies": [] # Puedes dejarlo vacío o llenarlo con el otro script
    }

    # 3. Actualizar JSONBin
    headers = {
        "X-Master-Key": JSONBIN_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"📤 SUBIENDO {len(noticias)} NOTICIAS A ELFILME...")
    res = requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID_NEWS}", json=payload, headers=headers)
    
    if res.status_code == 200:
        print("✅ NOTICIERO SINCRONIZADO CON ÉXITO.")
    else:
        print(f"❌ FALLO AL ACTUALIZAR: {res.text}")

if __name__ == "__main__":
    run()
