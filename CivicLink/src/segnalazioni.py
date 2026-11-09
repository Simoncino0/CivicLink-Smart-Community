"""
Modulo per la gestione delle segnalazioni del territorio.
"""
from datetime import date, datetime
from src.gestione_file import (
    SEGNALAZIONI_FILE,
    carica_json,
    salva_json,
    genera_nome_file_export,
    esporta_csv,
)

CATEGORIE_VALIDE = [
    "Illuminazione", "Strade", "Rifiuti",
    "Verde pubblico", "Sicurezza", "Altro",
]
PRIORITA_VALIDE = ["Bassa", "Media", "Alta"]
STATI_VALIDI = ["Aperta", "In lavorazione", "Risolta"]


def _valida_segnalazione(titolo, descrizione, categoria, zona, priorita):
    """Valida i campi della segnalazione."""
    if not isinstance(titolo, str) or not titolo.strip():
        return False, "Il titolo non puo essere vuoto."
    if not isinstance(descrizione, str) or not descrizione.strip():
        return False, "La descrizione non puo essere vuota."
    if categoria not in CATEGORIE_VALIDE:
        return False, f"Categoria non valida. Scegli tra: {', '.join(CATEGORIE_VALIDE)}"
    if not isinstance(zona, str) or not zona.strip():
        return False, "La zona non puo essere vuota."
    if priorita not in PRIORITA_VALIDE:
        return False, f"Priorita non valida. Scegli tra: {', '.join(PRIORITA_VALIDE)}"
    return True, ""


def aggiungi_segnalazione(titolo, descrizione, categoria, zona, priorita):
    """Aggiunge una nuova segnalazione. Restituisce (ok, messaggio)."""
    ok, msg = _valida_segnalazione(titolo, descrizione, categoria, zona, priorita)
    if not ok:
        return False, msg

    segnalazioni = carica_json(SEGNALAZIONI_FILE)
    ids = [s.get("id", 0) for s in segnalazioni]
    if any(not isinstance(id_record, int) or isinstance(id_record, bool)
           for id_record in ids):
        return False, "Errore: gli ID esistenti non sono interi validi."
    nuovo_id = max(ids, default=0) + 1

    nuova = {
        "id": nuovo_id,
        "titolo": titolo.strip(),
        "descrizione": descrizione.strip(),
        "categoria": categoria,
        "zona": zona.strip(),
        "priorita": priorita,
        "data": date.today().isoformat(),
        "stato": "Aperta",
    }

    segnalazioni.append(nuova)
    if salva_json(SEGNALAZIONI_FILE, segnalazioni):
        return True, f"Segnalazione #{nuovo_id} aggiunta con successo!"
    return False, "Errore nel salvataggio della segnalazione."


def visualizza_segnalazioni():
    """Restituisce la lista delle segnalazioni."""
    return carica_json(SEGNALAZIONI_FILE)


def modifica_stato(id_segnalazione, nuovo_stato):
    """Modifica lo stato di una segnalazione esistente."""
    if nuovo_stato not in STATI_VALIDI:
        return False, f"Stato non valido. Scegli tra: {', '.join(STATI_VALIDI)}"
    if isinstance(id_segnalazione, bool) or not isinstance(
        id_segnalazione, (int, str)
    ):
        return False, "L'ID deve essere un numero intero."
    try:
        id_segnalazione = int(id_segnalazione)
    except (TypeError, ValueError):
        return False, "L'ID deve essere un numero intero."

    segnalazioni = carica_json(SEGNALAZIONI_FILE)
    for s in segnalazioni:
        if s.get("id") == id_segnalazione:
            vecchio = s.get("stato", "N/D")
            s["stato"] = nuovo_stato
            s["data_aggiornamento"] = datetime.now().isoformat()
            if salva_json(SEGNALAZIONI_FILE, segnalazioni):
                return True, f"Stato aggiornato: '{vecchio}' -> '{nuovo_stato}'"
            return False, "Errore nel salvataggio."
    return False, f"Segnalazione con ID {id_segnalazione} non trovata."


def esporta_segnalazioni_csv():
    """Esporta le segnalazioni in CSV."""
    segnalazioni = carica_json(SEGNALAZIONI_FILE)
    if not segnalazioni:
        return False, "Nessuna segnalazione da esportare."
    headers = ["id", "titolo", "descrizione", "categoria", "zona",
               "priorita", "data", "stato"]
    filepath = genera_nome_file_export("segnalazioni")
    if esporta_csv(filepath, segnalazioni, headers):
        return True, f"Segnalazioni esportate in: {filepath}"
    return False, "Errore nell'esportazione CSV."