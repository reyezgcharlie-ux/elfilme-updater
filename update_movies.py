def run():
    hoy = datetime.now().weekday()
    headers_get = {"X-Master-Key": JSONBIN_KEY}
    res_get = requests.get(f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest", headers=headers_get)
    pelis_actuales = res_get.json()['record']

    # GENERAR SITEMAP SIEMPRE (Para evitar el error de GitHub)
    generar_sitemap(pelis_actuales)

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
        requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID}", json=movies, headers={"Content-Type": "application/json", "X-Master-Key": JSONBIN_KEY})
        generar_sitemap(movies) # Actualiza con las nuevas
        enviar_promo_editorial(movies[0]['title'], movies[0]['poster'], es_estreno=True)
    else: # RESTO DE LA SEMANA: SOLO MARKETING
        print("EJECUTANDO MARKETING DIARIO...")
        peli_promo = random.choice(pelis_actuales)
        enviar_promo_editorial(peli_promo['title'], peli_promo['poster'], es_estreno=False)
