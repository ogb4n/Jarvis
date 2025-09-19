#!/bin/bash
cd /home/graphene/Perso/Jarvis
source venv/bin/activate

echo "Démarrage du serveur Jarvis..."
python main.py &
SERVER_PID=$!

sleep 3

echo "Test de l'API..."
curl -s http://localhost:8000/ || echo "Erreur de connexion"

echo -e "\nArrêt du serveur..."
kill $SERVER_PID 2>/dev/null