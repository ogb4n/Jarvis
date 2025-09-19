#!/usr/bin/env python3
"""
Script pour lister et configurer les périphériques audio de Jarvis
Usage: python audio_devices.py [list|test|set <device_id>]
"""

import sys
import sounddevice as sd
import requests
import json

BASE_URL = "http://localhost:8000"

def list_system_devices():
    """Liste tous les périphériques audio du système"""
    print("🎤 Périphériques Audio Disponibles")
    print("=" * 50)
    
    try:
        devices = sd.query_devices()
        default_input = sd.default.device[0]
        default_output = sd.default.device[1]
        
        print(f"Périphérique d'entrée par défaut: {default_input}")
        print(f"Périphérique de sortie par défaut: {default_output}")
        print()
        
        print("ID | Nom                           | Entrée | Sortie | Fréq.")
        print("-" * 70)
        
        for i, device in enumerate(devices):
            name = device['name'][:30].ljust(30)
            max_in = str(device['max_input_channels']).rjust(6)
            max_out = str(device['max_output_channels']).rjust(6)
            rate = str(int(device['default_samplerate'])).rjust(5)
            
            marker = ""
            if i == default_input:
                marker += " [INPUT]"
            if i == default_output:
                marker += " [OUTPUT]"
            
            print(f"{i:2} | {name} | {max_in} | {max_out} | {rate}{marker}")
            
        return devices
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture des périphériques: {e}")
        return None

def test_jarvis_audio():
    """Teste les périphériques audio via l'API Jarvis"""
    print("🤖 Test des Périphériques Audio Jarvis")
    print("=" * 45)
    
    try:
        # Test de l'endpoint devices
        print("📡 Test de l'API périphériques...")
        response = requests.get(f"{BASE_URL}/api/audio/devices")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API périphériques fonctionnelle")
            print(f"Périphérique d'entrée actuel: {data.get('current_input_device', 'Défaut')}")
            print(f"Périphérique de sortie actuel: {data.get('current_output_device', 'Défaut')}")
            
            if 'devices' in data:
                print(f"Nombre de périphériques détectés: {len(data['devices'])}")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(response.text)
            
        # Test audio général
        print("\n🔊 Test des services audio...")
        response = requests.get(f"{BASE_URL}/api/audio/test")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Services audio fonctionnels")
                print(f"Test TTS: {'✅' if data.get('tts_test') else '❌'}")
            else:
                print(f"❌ Problème audio: {data.get('message', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur test audio: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter à {BASE_URL}")
        print("Assurez-vous que le serveur Jarvis fonctionne")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_device_recording(device_id):
    """Teste l'enregistrement sur un périphérique spécifique"""
    print(f"🎤 Test d'Enregistrement - Périphérique {device_id}")
    print("=" * 45)
    
    try:
        import numpy as np
        import time
        
        # Paramètres d'enregistrement
        duration = 3  # secondes
        sample_rate = 16000
        
        print(f"Enregistrement pendant {duration} secondes...")
        print("Parlez maintenant !")
        
        # Enregistrement
        recording = sd.rec(
            frames=duration * sample_rate,
            samplerate=sample_rate,
            channels=1,
            device=device_id,
            dtype=np.float32
        )
        
        sd.wait()  # Attendre la fin de l'enregistrement
        
        # Analyse basique
        rms = np.sqrt(np.mean(recording**2))
        max_amplitude = np.max(np.abs(recording))
        
        print(f"✅ Enregistrement terminé")
        print(f"RMS: {rms:.6f}")
        print(f"Amplitude max: {max_amplitude:.6f}")
        
        if rms > 0.001:
            print("✅ Signal audio détecté")
            
            # Test de lecture
            print("🔊 Lecture de l'enregistrement...")
            sd.play(recording, sample_rate)
            sd.wait()
            print("✅ Lecture terminée")
        else:
            print("⚠️  Signal audio très faible - vérifiez le micro")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

def show_usage():
    """Affiche l'usage du script"""
    print("Usage: python audio_devices.py [command]")
    print()
    print("Commands:")
    print("  list              - Liste tous les périphériques audio")
    print("  test              - Teste les services audio Jarvis")
    print("  record <device>   - Teste l'enregistrement sur un périphérique")
    print("  help              - Affiche cette aide")
    print()
    print("Exemples:")
    print("  python audio_devices.py list")
    print("  python audio_devices.py test")
    print("  python audio_devices.py record 0")

def main():
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_system_devices()
        
    elif command == "test":
        test_jarvis_audio()
        
    elif command == "record":
        if len(sys.argv) < 3:
            print("❌ Veuillez spécifier l'ID du périphérique")
            print("Usage: python audio_devices.py record <device_id>")
            sys.exit(1)
        
        try:
            device_id = int(sys.argv[2])
            test_device_recording(device_id)
        except ValueError:
            print("❌ L'ID du périphérique doit être un nombre")
            sys.exit(1)
            
    elif command == "help":
        show_usage()
        
    else:
        print(f"❌ Commande inconnue: {command}")
        show_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()