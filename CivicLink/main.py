"""
CivicLink - Smart Community
Python Innovation Hackathon

Applicazione da terminale per la gestione di segnalazioni territoriali
e oggetti smarriti/ritrovati in una comunita.

Architettura: Terminale -> Python -> JSON/CSV -> Frontend HTML (offline)
"""
import os
import sys
from datetime import datetime

# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.segnalazioni import (
    aggiungi_segnalazione, visualizza_segnalazioni, modifica_stato,
    esporta_segnalazioni_csv, CATEGORIE_VALIDE, PRIORITA_VALIDE, STATI_VALIDI,
)
from src.oggetti import (
    aggiungi_oggetto, visualizza_oggetti, modifica_stato_oggetto,
    esporta_oggetti_csv, TIPOLOGIE_VALIDE, ANNUNCI_VALIDI,
    STATI_VALIDI as STATI_OGGETTI,
)
from src.statistiche import stampa_statistiche, calcola_statistiche
from src.gestione_file import (
    SEGNALAZIONI_FILE, OGGETTI_FILE, salva_json,
    EXPORTS_DIR, inizializza_cartelle,
)


def _input_valido(prompt, opzioni):
    """Chiede un input e valida che sia tra le opzioni consentite."""
    while True:
        print(f"\n  Opzioni: {', '.join(opzioni)}")
        scelta = input(f"  {prompt}: ").strip()
        if scelta in opzioni:
            return scelta
        print(f"  Valore non valido. Scegli tra: {', '.join(opzioni)}")


def _input_non_vuoto(prompt, nome_campo):
    """Chiede un campo obbligatorio e ripete finche' non e' non vuoto."""
    while True:
        valore = input(prompt).strip()
        if valore:
            return valore
        print(f"  Il campo {nome_campo} non puo essere vuoto.")


def _carica_demo():
    """Carica dati di esempio nel sistema."""
    conferma = input("\n  ATTENZIONE: i dati esistenti verranno sovrascritti. "
                     "Continuare? (s/n): ").strip().lower()
    if conferma != "s":
        print("  Operazione annullata.")
        return

    print("  Caricamento dati demo...")

    segnalazioni_demo = [
        {"id": 1, "titolo": "Lampione rotto",
         "descrizione": "Il lampione in Via Roma 15 non funziona da una settimana.",
         "categoria": "Illuminazione", "zona": "Via Roma 15",
         "priorita": "Media", "data": "2026-10-28", "stato": "Aperta"},
        {"id": 2, "titolo": "Buca pericolosa",
         "descrizione": "Buca profonda sulla carreggiata, rischio per ciclisti.",
         "categoria": "Strade", "zona": "Via Garibaldi 42",
         "priorita": "Alta", "data": "2026-10-30", "stato": "In lavorazione"},
        {"id": 3, "titolo": "Cassonetto pieno",
         "descrizione": "Il cassonetto di Piazza Verdi e stracolmo.",
         "categoria": "Rifiuti", "zona": "Piazza Verdi",
         "priorita": "Media", "data": "2026-11-01", "stato": "Aperta"},
        {"id": 4, "titolo": "Ramo caduto",
         "descrizione": "Un grosso ramo e caduto sul marciapiede di Viale dei Tigli.",
         "categoria": "Verde pubblico", "zona": "Viale dei Tigli",
         "priorita": "Alta", "data": "2026-11-02", "stato": "Risolta"},
        {"id": 5, "titolo": "Atti vandalici",
         "descrizione": "Panchine danneggiate nel parco comunale.",
         "categoria": "Sicurezza", "zona": "Parco Comunale",
         "priorita": "Bassa", "data": "2026-11-03", "stato": "Aperta"},
    ]

    oggetti_demo = [
        {"id": 1, "nome": "Portafoglio nero",
         "descrizione": "Portafoglio in pelle con documenti all'interno.",
         "tipologia": "Documenti", "luogo": "Fermata autobus Via Mazzini",
         "annuncio": "Ritrovato", "data": "2026-11-04", "stato": "Attivo"},
        {"id": 2, "nome": "Mazzo di chiavi",
         "descrizione": "5 chiavi con portachiavi rosso.",
         "tipologia": "Chiavi", "luogo": "Parco giochi comunale",
         "annuncio": "Smarrito", "data": "2026-11-03", "stato": "Attivo"},
        {"id": 3, "nome": "Smartphone",
         "descrizione": "Smartphone Android con cover blu.",
         "tipologia": "Elettronica", "luogo": "Biblioteca civica",
         "annuncio": "Ritrovato", "data": "2026-11-02", "stato": "Risolto"},
    ]

    segnalazioni_salvate = salva_json(SEGNALAZIONI_FILE, segnalazioni_demo)
    oggetti_salvati = salva_json(OGGETTI_FILE, oggetti_demo)
    if segnalazioni_salvate:
        print(f"  Caricate {len(segnalazioni_demo)} segnalazioni demo.")
    else:
        print("  Errore nel caricamento delle segnalazioni demo.")
    if oggetti_salvati:
        print(f"  Caricati {len(oggetti_demo)} oggetti demo.")
    else:
        print("  Errore nel caricamento degli oggetti demo.")


def _stampa_segnalazioni(segnalazioni):
    """Stampa la lista segnalazioni in formato tabellare."""
    if not segnalazioni:
        print("\n  Nessuna segnalazione presente.")
        return
    print("\n" + "-" * 80)
    print(f"  {'ID':<4} {'Titolo':<25} {'Categoria':<15} {'Priorita':<10} {'Stato':<12}")
    print("-" * 80)
    for s in segnalazioni:
        titolo = str(s.get("titolo", "N/D"))[:24]
        print(f"  {s.get('id', 'N/D')!s:<4} {titolo:<25} "
              f"{s.get('categoria', 'N/D')!s:<15} "
              f"{s.get('priorita', 'N/D')!s:<10} "
              f"{s.get('stato', 'N/D')!s:<12}")
    print("-" * 80)


def _stampa_oggetti(oggetti):
    """Stampa la lista oggetti in formato tabellare."""
    if not oggetti:
        print("\n  Nessun oggetto presente.")
        return
    print("\n" + "-" * 85)
    print(f"  {'ID':<4} {'Nome':<20} {'Tipologia':<12} {'Annuncio':<10} "
          f"{'Luogo':<20} {'Stato':<8}")
    print("-" * 85)
    for o in oggetti:
        nome = str(o.get("nome", "N/D"))[:19]
        luogo = str(o.get("luogo", "N/D"))[:19]
        print(f"  {o.get('id', 'N/D')!s:<4} {nome:<20} "
              f"{o.get('tipologia', 'N/D')!s:<12} "
              f"{o.get('annuncio', 'N/D')!s:<10} {luogo:<20} "
              f"{o.get('stato', 'N/D')!s:<8}")
    print("-" * 85)


def menu_segnalazioni():
    """Menu per inserire una nuova segnalazione."""
    print("\n  NUOVA SEGNALAZIONE")
    print("  " + "-" * 40)
    titolo = _input_non_vuoto("  Titolo: ", "titolo")
    descrizione = _input_non_vuoto("  Descrizione: ", "descrizione")
    categoria = _input_valido("Categoria", CATEGORIE_VALIDE)
    zona = _input_non_vuoto("  Zona / Indirizzo: ", "zona")
    priorita = _input_valido("Priorita", PRIORITA_VALIDE)

    ok, msg = aggiungi_segnalazione(titolo, descrizione, categoria, zona, priorita)
    print(f"  {msg}")


def menu_modifica_stato():
    """Menu per modificare lo stato di una segnalazione."""
    print("\n  MODIFICA STATO SEGNALAZIONE")
    print("  " + "-" * 40)
    segnalazioni = visualizza_segnalazioni()
    _stampa_segnalazioni(segnalazioni)
    if not segnalazioni:
        return

    id_scelto = input("\n  ID della segnalazione da modificare: ").strip()

    try:
        id_num = int(id_scelto)
    except ValueError:
        print("  L'ID deve essere un numero intero.")
        return

    esiste = any(s.get("id") == id_num for s in segnalazioni)
    if not esiste:
        print(f"  Segnalazione con ID {id_scelto} non trovata.")
        return

    nuovo_stato = _input_valido("Nuovo stato", STATI_VALIDI)
    ok, msg = modifica_stato(id_scelto, nuovo_stato)
    print(f"  {msg}")


def menu_oggetti():
    """Menu per registrare un nuovo oggetto."""
    print("\n  NUOVO OGGETTO SMARRITO / RITROVATO")
    print("  " + "-" * 40)
    nome = _input_non_vuoto("  Nome dell'oggetto: ", "nome")
    descrizione = _input_non_vuoto("  Descrizione: ", "descrizione")
    tipologia = _input_valido("Tipologia", TIPOLOGIE_VALIDE)
    luogo = _input_non_vuoto("  Luogo: ", "luogo")
    annuncio = _input_valido("Tipo annuncio", ANNUNCI_VALIDI)

    ok, msg = aggiungi_oggetto(nome, descrizione, tipologia, luogo, annuncio)
    print(f"  {msg}")


def menu_visualizza_oggetti():
    """Menu per visualizzare gli oggetti e modificarne lo stato."""
    print("\n  ELENCO OGGETTI")
    print("  " + "-" * 40)
    oggetti = visualizza_oggetti()
    _stampa_oggetti(oggetti)

    if not oggetti:
        return

    while True:
        scelta = input("\n  Vuoi modificare lo stato di un oggetto? (s/n): ").strip().lower()
        if scelta in ("s", "n"):
            break
        print("  Risposta non valida. Digita 's' o 'n'.")

    if scelta == "s":
        id_scelto = input("  ID dell'oggetto: ").strip()

        try:
            id_num = int(id_scelto)
            esiste = any(o.get("id") == id_num for o in oggetti)
            if not esiste:
                print(f"  Oggetto con ID {id_scelto} non trovato.")
                return
        except ValueError:
            print("  L'ID deve essere un numero intero.")
            return

        nuovo_stato = _input_valido("Nuovo stato", STATI_OGGETTI)
        ok, msg = modifica_stato_oggetto(id_scelto, nuovo_stato)
        print(f"  {msg}")


def menu_esporta():
    """Esporta i dati in JSON e CSV."""
    print("\n  ESPORTAZIONE DATI")
    print("  " + "-" * 40)

    print("\n  Esportazione JSON per la dashboard...")
    segnalazioni = visualizza_segnalazioni()
    oggetti = visualizza_oggetti()
    stats = calcola_statistiche()

    dashboard_data = {
        "meta": {
            "progetto": "CivicLink",
            "versione": "1.0.0",
            "data_esportazione": datetime.now().isoformat(),
        },
        "statistiche": stats,
        "segnalazioni": segnalazioni,
        "oggetti": oggetti,
    }

    json_export = EXPORTS_DIR / "dashboard_data.json"
    if salva_json(json_export, dashboard_data):
        print(f"  JSON dashboard salvato in: {json_export}")
    else:
        print("  Errore nel salvataggio JSON dashboard.")

    print("\n  Esportazione CSV...")
    ok1, msg1 = esporta_segnalazioni_csv()
    print(f"  {msg1}")
    ok2, msg2 = esporta_oggetti_csv()
    print(f"  {msg2}")


def menu_istruzioni():
    """Mostra le istruzioni per la dashboard."""
    print("\n" + "=" * 60)
    print("  ISTRUZIONI PER LA DASHBOARD WEB")
    print("=" * 60)
    print("""
  1. Seleziona l'opzione 7 per esportare i dati in JSON.

  2. Il file 'dashboard_data.json' verra creato in:
     data/exports/

  3. Apri il file 'frontend/index.html' nel tuo browser.

  4. Clicca sul pulsante 'Carica Dati' e seleziona
     il file 'dashboard_data.json' appena esportato.

  5. La dashboard visualizzera statistiche,
     segnalazioni e oggetti smarriti/ritrovati.

  La dashboard funziona completamente OFFLINE.
  Non richiede server, internet o database.
""")
    print("=" * 60)
    input("  Premi INVIO per tornare al menu...")


def menu_principale():
    """Menu principale dell'applicazione."""
    inizializza_cartelle()

    while True:
        print("\n" + "=" * 60)
        print("  CIVICLINK - SMART COMMUNITY")
        print("=" * 60)
        print("  1. Inserisci una nuova segnalazione")
        print("  2. Visualizza tutte le segnalazioni")
        print("  3. Modifica lo stato di una segnalazione")
        print("  4. Registra un oggetto smarrito o ritrovato")
        print("  5. Visualizza gli oggetti")
        print("  6. Visualizza statistiche")
        print("  7. Esporta dati in JSON e CSV")
        print("  8. Apri le istruzioni per la dashboard")
        print("  9. Carica dati DEMO (esempi)")
        print("  0. Esci")
        print("=" * 60)

        scelta = input("\n  Scegli un'opzione: ").strip()

        if scelta == "1":
            menu_segnalazioni()
        elif scelta == "2":
            print("\n  ELENCO SEGNALAZIONI")
            _stampa_segnalazioni(visualizza_segnalazioni())
        elif scelta == "3":
            menu_modifica_stato()
        elif scelta == "4":
            menu_oggetti()
        elif scelta == "5":
            menu_visualizza_oggetti()
        elif scelta == "6":
            stampa_statistiche()
        elif scelta == "7":
            menu_esporta()
        elif scelta == "8":
            menu_istruzioni()
        elif scelta == "9":
            _carica_demo()
        elif scelta == "0":
            print("\n  Grazie per aver usato CivicLink! A presto.")
            break
        else:
            print("  Opzione non valida. Riprova.")


if __name__ == "__main__":
    try:
        menu_principale()
    except KeyboardInterrupt:
        print("\n\n  Programma interrotto dall'utente. A presto!")
    except Exception as e:
        print(f"\n  Errore imprevisto: {e}")