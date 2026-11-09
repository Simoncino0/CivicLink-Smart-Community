"""
Modulo per il calcolo delle statistiche.
"""
from src.gestione_file import SEGNALAZIONI_FILE, OGGETTI_FILE, carica_json


def calcola_statistiche():
    """Calcola e restituisce un dizionario con tutte le statistiche."""
    segnalazioni = carica_json(SEGNALAZIONI_FILE)
    oggetti = carica_json(OGGETTI_FILE)

    stats = {
        "totale_segnalazioni": len(segnalazioni),
        "segnalazioni_aperte": 0,
        "segnalazioni_in_lavorazione": 0,
        "segnalazioni_risolte": 0,
        "categoria_piu_frequente": "N/D",
        "totale_oggetti": len(oggetti),
        "oggetti_smarriti": 0,
        "oggetti_ritrovati": 0,
    }

    categorie_count = {}
    for s in segnalazioni:
        stato = s.get("stato", "Aperta")
        categoria = s.get("categoria", "Altro")
        if not isinstance(categoria, str) or not categoria.strip():
            categoria = "Altro"

        if stato == "Aperta":
            stats["segnalazioni_aperte"] += 1
        elif stato == "In lavorazione":
            stats["segnalazioni_in_lavorazione"] += 1
        elif stato == "Risolta":
            stats["segnalazioni_risolte"] += 1

        categorie_count[categoria] = categorie_count.get(categoria, 0) + 1

    if categorie_count:
        stats["categoria_piu_frequente"] = max(
            categorie_count, key=categorie_count.get
        )

    for o in oggetti:
        annuncio = o.get("annuncio", "")
        if annuncio == "Smarrito":
            stats["oggetti_smarriti"] += 1
        elif annuncio == "Ritrovato":
            stats["oggetti_ritrovati"] += 1

    return stats


def stampa_statistiche():
    """Stampa le statistiche in formato leggibile."""
    stats = calcola_statistiche()

    print("\n" + "=" * 50)
    print("  STATISTICHE CIVICLINK")
    print("=" * 50)
    print("\nSEGNALAZIONI DEL TERRITORIO:")
    print(f"   Totale:          {stats['totale_segnalazioni']}")
    print(f"   Aperte:          {stats['segnalazioni_aperte']}")
    print(f"   In lavorazione:  {stats['segnalazioni_in_lavorazione']}")
    print(f"   Risolte:         {stats['segnalazioni_risolte']}")
    print(f"   Categoria top:   {stats['categoria_piu_frequente']}")
    print("\nOGGETTI SMARRITI / RITROVATI:")
    print(f"   Totale oggetti:  {stats['totale_oggetti']}")
    print(f"   Smarriti:        {stats['oggetti_smarriti']}")
    print(f"   Ritrovati:       {stats['oggetti_ritrovati']}")
    print("=" * 50)
    return stats