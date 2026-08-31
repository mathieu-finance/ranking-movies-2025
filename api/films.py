"""
Fonction serverless Vercel (Python runtime).
Endpoint : GET /api/films

Interroge l'API TMDb (discover/movie + movie/{id}) pour les films sortis en
2025, calcule le ratio de rentabilité (recettes mondiales / budget) et
renvoie un JSON trié.

Variable d'environnement requise sur Vercel : TMDB_API_KEY
(Project Settings -> Environment Variables)
"""

import json
import os
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

TMDB_BASE = "https://api.themoviedb.org/3"
PAGES_A_PARCOURIR = 5          # 20 films/page côté TMDb
BUDGET_MIN_USD = 1_000_000     # écarte les budgets aberrants/mal renseignés


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=20) as resp:
        return json.loads(resp.read().decode())


def _discover_films_2025(api_key: str) -> list[dict]:
    resultats = []
    for page in range(1, PAGES_A_PARCOURIR + 1):
        params = {
            "api_key": api_key,
            "language": "fr-FR",
            "sort_by": "revenue.desc",
            "primary_release_year": 2025,
            "page": page,
        }
        url = f"{TMDB_BASE}/discover/movie?{urllib.parse.urlencode(params)}"
        data = _get_json(url)
        resultats.extend(data.get("results", []))
        if page >= data.get("total_pages", 1):
            break
    return resultats


def _details_film(api_key: str, film_id: int) -> dict:
    params = {"api_key": api_key, "language": "fr-FR"}
    url = f"{TMDB_BASE}/movie/{film_id}?{urllib.parse.urlencode(params)}"
    return _get_json(url)


def _construire_classement(api_key: str) -> list[dict]:
    resumes = _discover_films_2025(api_key)
    films = []

    for resume in resumes:
        details = _details_film(api_key, resume["id"])
        budget = details.get("budget") or 0
        recettes = details.get("revenue") or 0

        if budget < BUDGET_MIN_USD or recettes <= 0:
            continue

        films.append({
            "titre": details.get("title"),
            "date_sortie": details.get("release_date"),
            "budget_usd": budget,
            "recettes_mondiales_usd": recettes,
            "ratio_rentabilite": round(recettes / budget, 2),
            "profit_brut_usd": recettes - budget,
            "affiche": (
                f"https://image.tmdb.org/t/p/w342{details['poster_path']}"
                if details.get("poster_path") else None
            ),
        })
        time.sleep(0.05)

    films.sort(key=lambda f: f["ratio_rentabilite"], reverse=True)
    return films


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        api_key = os.environ.get("TMDB_API_KEY")

        if not api_key:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Variable d'environnement TMDB_API_KEY manquante sur Vercel."
            }).encode())
            return

        try:
            classement = _construire_classement(api_key)
            corps = json.dumps({"films": classement}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "s-maxage=3600")  # cache 1h côté Vercel
            self.end_headers()
            self.wfile.write(corps)
        except Exception as exc:  # noqa: BLE001
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode())
