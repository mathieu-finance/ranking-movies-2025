# Box-Office 2025 — Classement de rentabilité

Petit site qui affiche un classement des films sortis en 2025, triés par
**rentabilité réelle** (recettes mondiales ÷ budget), à partir de l'API
publique [TMDb](https://www.themoviedb.org/).

- `index.html` — page front-end (aucun framework, HTML/CSS/JS natifs).
- `api/films.py` — fonction serverless Python (Vercel) qui interroge TMDb,
  calcule le ratio de rentabilité, et renvoie du JSON.

## 1. Obtenir une clé TMDb (gratuite)

1. Créer un compte sur https://www.themoviedb.org/signup
2. Aller dans *Paramètres → API* : https://www.themoviedb.org/settings/api
3. Générer une clé API (v3 auth).

## 2. Déployer sur GitHub

```bash
cd classement-films-2025
git init
git add .
git commit -m "Classement box-office 2025 (TMDb)"
git branch -M main
git remote add origin https://github.com/<TON_COMPTE_GITHUB>/classement-films-2025.git
git push -u origin main
```

(Remplace `<TON_COMPTE_GITHUB>` par ton nom d'utilisateur GitHub — à créer au
préalable sur github.com si ce n'est pas déjà fait.)

## 3. Déployer sur Vercel

1. Aller sur https://vercel.com et se connecter (avec le compte souhaité).
2. **Add New → Project**, puis importer le dépôt GitHub créé à l'étape 2.
3. Dans **Environment Variables**, ajouter :
   - `TMDB_API_KEY` = ta clé obtenue à l'étape 1
4. Cliquer sur **Deploy**. Vercel détecte automatiquement `index.html` (site
   statique) et `api/films.py` (fonction Python serverless).

Une fois déployé, le site est accessible à une URL du type
`https://classement-films-2025.vercel.app`, avec le classement calculé en
direct à chaque visite (mis en cache 1h côté serveur).

## Notes

- Les budgets/recettes TMDb sont déclaratifs et communautaires : à prendre
  comme ordre de grandeur, pas comme chiffres officiels audités.
- Les films avec un budget déclaré < 1 000 000 $ sont écartés du classement
  (souvent des données mal renseignées qui faussent le ratio).
- Pour un usage en base de données SQL classique (hors site web), voir les
  scripts `tmdb_extraction_2025.py` / `classement_tmdb_2025.sql` fournis
  précédemment dans la conversation.
