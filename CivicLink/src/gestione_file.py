"""Modulo per la gestione dei file JSON e CSV."""
import json
import csv
import os
from datetime import datetime
from pathlib import Path

# Percorsi assoluti basati sulla posizione del progetto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXPORTS_DIR = DATA_DIR / "exports"
SEGNALAZIONI_FILE = DATA_DIR / "segnalazioni.json"
OGGETTI_FILE = DATA_DIR / "oggetti.json"


def inizializza_cartelle():
    """Crea le cartelle necessarie se non esistono."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def carica_json(filepath):
    """Carica i dati da un file JSON. Restituisce lista vuota in caso di errore."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            dati = json.load(f)
            if not isinstance(dati, list) or any(
                not isinstance(riga, dict) for riga in dati
            ):
                print(
                    f"Attenzione: {filepath} non contiene una lista valida "
                    "di record JSON. "
                    "Uso lista vuota."
                )
                return []
            return dati
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(
            f"Attenzione: {filepath} e' corrotto o non valido. "
            "Uso lista vuota."
        )
        print(
            f"L'ultima copia buona potrebbe essere nel backup {filepath}.bak."
        )
        return []
    except IOError as errore:
        print(f"Errore di lettura del file {filepath}: {errore}")
        return []


def salva_json(filepath, dati):
    """Salva i dati in JSON. Crea un backup prima di sovrascrivere."""
    try:
        contenuto = json.dumps(dati, indent=2, ensure_ascii=False)
    except (TypeError, ValueError) as errore:
        print(f"Errore: dati non serializzabili in JSON: {errore}")
        return False

    try:
        # Backup del file esistente
        if os.path.exists(filepath):
            backup = str(filepath) + ".bak"
            with open(filepath, "r", encoding="utf-8") as src:
                content = src.read()
            with open(backup, "w", encoding="utf-8") as dst:
                dst.write(content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(contenuto)
        return True
    except OSError as errore:
        print(f"Errore di scrittura del file {filepath}: {errore}")
        return False


def esporta_csv(filepath, dati, headers):
    """Esporta una lista di dizionari in CSV."""
    try:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            for riga in dati:
                writer.writerow(riga)
        return True
    except IOError:
        return False


def genera_nome_file_export(tipo):
    """Genera un nome file con timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return EXPORTS_DIR / f"{tipo}_{timestamp}.csv"


inizializza_cartelle()