# CivicLink — Smart Community

Progetto per il **Python Innovation Hackathon** — tema *Smart Community*.
Segnalazioni territoriali e oggetti smarriti o ritrovati: backend Python da terminale + dashboard web offline in HTML/CSS/JavaScript vanilla.

## Cosa fa

- Inserisce e gestisce segnalazioni territoriali (illuminazione, strade, rifiuti, verde pubblico, sicurezza)
- Registra oggetti smarriti e ritrovati
- Aggiorna lo stato delle pratiche (Aperta / In lavorazione / Risolta)
- Esporta i dati in JSON e CSV
- Li visualizza in una dashboard offline con grafici, filtri e ricerca

## Struttura della repository

- `CivicLink/` — codice del progetto
  - `main.py` — menu e flusso principale
  - `src/` — moduli Python (segnalazioni, oggetti, statistiche, gestione file)
  - `tests/` — 17 test automatici unittest
  - `frontend/` — dashboard HTML/CSS/JS
  - `data/` — dati JSON ed export
- `Presentazione/` — materiale per la presentazione finale
- `Project_Brief.pdf` — ideazione, target, MVP e piano di lavoro
- `Kanban_Checkpoint.pdf` — kanban e checkpoint CP1/CP2/CP3
- `Report_Test.pdf` — report dei test con input, atteso e osservato

Documentazione tecnica dettagliata in `CivicLink/README.md`.

## Avvio rapido

1. Backend: entrare in `CivicLink/` ed eseguire `python main.py`
2. Test automatici: `python -m unittest tests.test_backend -v`
3. Dashboard: aprire `CivicLink/frontend/index.html` nel browser e caricare `CivicLink/data/exports/dashboard_data.json`

## Vincoli rispettati

Solo standard library Python · HTML/CSS/JS vanilla · nessun server, API o database · caricamento JSON manuale con FileReader · funzionamento 100% offline

## Team

Davide Storelli · Pietro Russo · Simone Stellabotte · Emanuele Timbo
