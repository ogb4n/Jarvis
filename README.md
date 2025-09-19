# Jarvis
# Jarvis

Assistant vocal auto-hébergé, multi-pièce, open-source.

## Lancement rapide

```bash
git clone https://github.com/ogb4n/jarvis
cd jarvis
cp .env.example .env  # si besoin
pip install -r requirements.txt
python main.py
```

## Stack technique
- Python 3.11
- FastAPI
- MongoDB (pymongo)
- MQTT, Websockets
- Whisper, pyttsx3

## Structure du projet

```
jarvis/
	core/
	services/
	models/
	utils/
	tests/
```

## Fonctionnalités prévues
- Commandes vocales
- Historique et logs
- Modularité satellites
- Recherche full-text
- API REST

## Licence
MIT
