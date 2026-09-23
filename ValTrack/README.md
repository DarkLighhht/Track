# VALORANT Flask Tracker

## Local
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python app.py

## Render
Build: pip install -r requirements.txt
Start: gunicorn app:app

Environment variables: FLASK_SECRET_KEY, RIOT_CLIENT_ID, RIOT_CLIENT_SECRET, RIOT_REDIRECT_URI, RIOT_REGION.
Replace riot.txt with the exact verification string from Riot.
Never commit .env.
