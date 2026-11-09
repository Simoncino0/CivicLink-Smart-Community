"""
Modulo per la gestione degli oggetti smarriti e ritrovati.
"""
from datetime import date
from src.gestione_file import (
    OGGETTI_FILE,
    carica_json,
    salva_json,
    genera_nome_file_export,
    esporta_csv,
)

TIPOLOGIE_VALIDE = ["Documenti", "Chiavi", "Elettronica", "Accessori", "Altro"]
ANNUNCI_VALIDI = ["Smarrito", "Ritrovato"]
STATI_VALIDI = ["Attivo", "Risolto"]


def _valida_oggetto(nome, descrizione, tipologia, luogo, annuncio):
    """Valida i campi dell'oggetto."""
    if not isinstance(nome, str) or not nome.strip():
        return False, "Il nome dell'oggetto non puo essere vuoto."
    if not isinstance(descrizione, str) or not descrizione.strip():
        return False, "La descrizione non puo essere vuota."
    if tipologia not in TIPOLOGIE_VALIDE:
        return False, f"Tipologia non valida. Scegli tra: {', '.join(TIPOLOGIE_VALIDE)}"
    if not isinstance(luogo, str) or not luogo.strip():
        return False, "Il luogo non puo essere vuoto."
    if annuncio not in ANNUNCI_VALIDI:
        return False, f"Tipo annuncio non valido. Scegli tra: {', '.join(ANNUNCI_VALIDI)}"
    return True, ""


def aggiungi_oggetto(nome, descrizione, tipologia, luogo, annuncio):
    """Aggiunge un nuovo oggetto smarrito/ritrovato."""
    ok, msg = _valida_oggetto(nome, descrizione, tipologia, luogo, annuncio)
    if not ok:
        return False, msg

    oggetti = carica_json(OGGETTI_FILE)
    ids = [o.get("id", 0) for o in oggetti]
    if any(not isinstance(id_record, int) or isinstance(id_record, bool)
           for id_record in ids):
        return False, "Errore: gli ID esistenti non sono interi validi."
    nuovo_id = max(ids, default=0) + 1

    nuovo = {
        "id": nuovo_id,
        "nome": nome.strip(),
        "descrizione": descrizione.strip(),
        "tipologia": tipologia,
        "luogo": luogo.strip(),
        "annuncio": annuncio,
        "data": date.today().isoformat(),
        "stato": "Attivo",
    }

    oggetti.append(nuovo)
    if salva_json(OGGETTI_FILE, oggetti):
        return True, f"Oggetto #{nuovo_id} registrato con successo!"
    return False, "Errore nel salvataggio dell'oggetto."


def visualizza_oggetti():
    """Restituisce la lista degli oggetti."""
    return carica_json(OGGETTI_FILE)


def modifica_stato_oggetto(id_oggetto, nuovo_stato):
    """Modifica lo stato di un oggetto."""
    if nuovo_stato not in STATI_VALIDI:
        return False, f"Stato non valido. Scegli tra: {', '.join(STATI_VALIDI)}"
    if isinstance(id_oggetto, bool) or not isinstance(id_oggetto, (int, str)):
        return False, "L'ID deve essere un numero intero."
    try:
        id_oggetto = int(id_oggetto)
    except (TypeError, ValueError):
        return False, "L'ID deve essere un numero intero."

    oggetti = carica_json(OGGETTI_FILE)
    for o in oggetti:
        if o.get("id") == id_oggetto:
            vecchio = o.get("stato", "N/D")
            o["stato"] = nuovo_stato
            if salva_json(OGGETTI_FILE, oggetti):
                return True, f"Stato aggiornato: '{vecchio}' -> '{nuovo_stato}'"
            return False, "Errore nel salvataggio."
    return False, f"Oggetto con ID {id_oggetto} non trovato."


def esporta_oggetti_csv():
    """Esporta gli oggetti in CSV."""
    oggetti = carica_json(OGGETTI_FILE)
    if not oggetti:
        return False, "Nessun oggetto da esportare."
    headers = ["id", "nome", "descrizione", "tipologia", "luogo",
               "annuncio", "data", "stato"]
    filepath = genera_nome_file_export("oggetti")
    if esporta_csv(filepath, oggetti, headers):
        return True, f"Oggetti esportati in: {filepath}"
    return False, "Errore nell'esportazione CSV."