"""Test automatici per il backend CivicLink."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import gestione_file, oggetti, segnalazioni, statistiche


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.segnalazioni_file = self.root / "segnalazioni.json"
        self.oggetti_file = self.root / "oggetti.json"
        self.exports_dir = self.root / "exports"
        self.exports_dir.mkdir()

        self._patch_constants()

    def _patch_constants(self):
        for module in (gestione_file, segnalazioni, statistiche):
            patcher = patch.object(
                module, "SEGNALAZIONI_FILE", self.segnalazioni_file
            )
            patcher.start()
            self.addCleanup(patcher.stop)

        for module in (gestione_file, oggetti, statistiche):
            patcher = patch.object(module, "OGGETTI_FILE", self.oggetti_file)
            patcher.start()
            self.addCleanup(patcher.stop)

        patcher = patch.object(gestione_file, "EXPORTS_DIR", self.exports_dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_aggiunta_segnalazione_valida(self):
        ok, messaggio = segnalazioni.aggiungi_segnalazione(
            "Lampione spento",
            "Il lampione non funziona",
            "Illuminazione",
            "Via Roma",
            "Media",
        )

        self.assertTrue(ok, messaggio)
        self.assertEqual(segnalazioni.visualizza_segnalazioni()[0]["id"], 1)

    def test_rifiuta_campi_segnalazione_vuoti(self):
        casi = (
            ("", "Descrizione", "Via Roma"),
            ("Titolo", " ", "Via Roma"),
            ("Titolo", "Descrizione", ""),
        )
        for titolo, descrizione, zona in casi:
            with self.subTest(
                titolo=titolo, descrizione=descrizione, zona=zona
            ):
                ok, _ = segnalazioni.aggiungi_segnalazione(
                    titolo, descrizione, "Illuminazione", zona, "Media"
                )
                self.assertFalse(ok)

    def test_rifiuta_categoria_e_priorita_non_valide(self):
        casi = (
            ("Non valida", "Media"),
            ("Illuminazione", "Urgente"),
        )
        for categoria, priorita in casi:
            with self.subTest(categoria=categoria, priorita=priorita):
                ok, _ = segnalazioni.aggiungi_segnalazione(
                    "Titolo",
                    "Descrizione",
                    categoria,
                    "Via Roma",
                    priorita,
                )
                self.assertFalse(ok)

    def test_aggiunta_oggetti_smarrito_e_ritrovato(self):
        for annuncio in ("Smarrito", "Ritrovato"):
            with self.subTest(annuncio=annuncio):
                ok, messaggio = oggetti.aggiungi_oggetto(
                    "Chiavi",
                    "Un mazzo di chiavi",
                    "Chiavi",
                    "Piazza centrale",
                    annuncio,
                )
                self.assertTrue(ok, messaggio)

        annunci_salvati = [
            item["annuncio"] for item in oggetti.visualizza_oggetti()
        ]
        self.assertEqual(annunci_salvati, ["Smarrito", "Ritrovato"])

    def test_rifiuta_campi_oggetto_vuoti(self):
        casi = (
            ("", "Descrizione", "Via Roma"),
            ("Nome", " ", "Via Roma"),
            ("Nome", "Descrizione", ""),
        )
        for nome, descrizione, luogo in casi:
            with self.subTest(nome=nome, descrizione=descrizione, luogo=luogo):
                ok, _ = oggetti.aggiungi_oggetto(
                    nome, descrizione, "Chiavi", luogo, "Smarrito"
                )
                self.assertFalse(ok)

    def test_rifiuta_tipologia_e_annuncio_non_validi(self):
        casi = (
            ("Non valida", "Smarrito"),
            ("Chiavi", "In prestito"),
        )
        for tipologia, annuncio in casi:
            with self.subTest(tipologia=tipologia, annuncio=annuncio):
                ok, _ = oggetti.aggiungi_oggetto(
                    "Nome",
                    "Descrizione",
                    tipologia,
                    "Via Roma",
                    annuncio,
                )
                self.assertFalse(ok)

    def test_menu_segnalazioni_ripete_input_titolo_vuoto(self):
        import main

        with (
            patch(
                "main.input",
                side_effect=[
                    "",
                    "Titolo valido",
                    "Descrizione valida",
                    "Zona valida",
                ],
            ),
            patch(
                "main._input_valido",
                side_effect=["Illuminazione", "Media"],
            ),
            patch(
                "main.aggiungi_segnalazione", return_value=(True, "ok")
            ) as aggiungi,
        ):
            main.menu_segnalazioni()

        aggiungi.assert_called_once_with(
            "Titolo valido",
            "Descrizione valida",
            "Illuminazione",
            "Zona valida",
            "Media",
        )

    def test_menu_oggetti_ripete_input_nome_vuoto(self):
        import main

        with (
            patch(
                "main.input",
                side_effect=[
                    "",
                    "Nome valido",
                    "Descrizione valida",
                    "Luogo valido",
                ],
            ),
            patch(
                "main._input_valido", side_effect=["Chiavi", "Smarrito"]
            ),
            patch(
                "main.aggiungi_oggetto", return_value=(True, "ok")
            ) as aggiungi,
        ):
            main.menu_oggetti()

        aggiungi.assert_called_once_with(
            "Nome valido",
            "Descrizione valida",
            "Chiavi",
            "Luogo valido",
            "Smarrito",
        )

    def test_modifica_stato_segnalazione_con_id_esistente(self):
        segnalazioni.aggiungi_segnalazione(
            "Titolo", "Descrizione", "Strade", "Via Roma", "Bassa"
        )

        ok, _ = segnalazioni.modifica_stato("1", "Risolta")

        self.assertTrue(ok)
        self.assertEqual(
            segnalazioni.visualizza_segnalazioni()[0]["stato"], "Risolta"
        )

    def test_modifica_stato_segnalazione_con_id_inesistente(self):
        ok, messaggio = segnalazioni.modifica_stato("99", "Risolta")

        self.assertFalse(ok)
        self.assertIn("non trovata", messaggio)

    def test_modifica_stato_segnalazione_con_id_non_intero(self):
        ok, messaggio = segnalazioni.modifica_stato("abc", "Risolta")

        self.assertFalse(ok)
        self.assertIn("numero intero", messaggio)

    def test_modifica_stato_oggetto_con_id_esistente_inesistente_e_non_intero(
        self,
    ):
        oggetti.aggiungi_oggetto(
            "Chiavi", "Descrizione", "Chiavi", "Via Roma", "Ritrovato"
        )

        ok, _ = oggetti.modifica_stato_oggetto("1", "Risolto")
        self.assertTrue(ok)
        self.assertEqual(oggetti.visualizza_oggetti()[0]["stato"], "Risolto")

        ok, messaggio = oggetti.modifica_stato_oggetto("99", "Risolto")
        self.assertFalse(ok)
        self.assertIn("non trovato", messaggio)

        ok, messaggio = oggetti.modifica_stato_oggetto("abc", "Risolto")
        self.assertFalse(ok)
        self.assertIn("numero intero", messaggio)

    def test_statistiche_su_dataset_noto(self):
        gestione_file.salva_json(
            self.segnalazioni_file,
            [
                {"id": 1, "stato": "Aperta", "categoria": "Strade"},
                {"id": 2, "stato": "In lavorazione", "categoria": "Strade"},
                {"id": 3, "stato": "Risolta", "categoria": "Verde pubblico"},
            ],
        )
        gestione_file.salva_json(
            self.oggetti_file,
            [
                {"id": 1, "annuncio": "Smarrito"},
                {"id": 2, "annuncio": "Ritrovato"},
                {"id": 3, "annuncio": "Ritrovato"},
            ],
        )

        self.assertEqual(
            statistiche.calcola_statistiche(),
            {
                "totale_segnalazioni": 3,
                "segnalazioni_aperte": 1,
                "segnalazioni_in_lavorazione": 1,
                "segnalazioni_risolte": 1,
                "categoria_piu_frequente": "Strade",
                "totale_oggetti": 3,
                "oggetti_smarriti": 1,
                "oggetti_ritrovati": 2,
            },
        )

    def test_export_csv_con_header_corretti(self):
        segnalazioni.aggiungi_segnalazione(
            "Titolo", "Descrizione", "Strade", "Via Roma", "Media"
        )
        oggetti.aggiungi_oggetto(
            "Chiavi", "Descrizione", "Chiavi", "Via Roma", "Smarrito"
        )
        segnalazioni_csv = self.root / "segnalazioni.csv"
        oggetti_csv = self.root / "oggetti.csv"

        with patch.object(
            segnalazioni,
            "genera_nome_file_export",
            return_value=segnalazioni_csv,
        ):
            ok_segnalazioni, msg_segnalazioni = (
                segnalazioni.esporta_segnalazioni_csv()
            )
        with patch.object(
            oggetti, "genera_nome_file_export", return_value=oggetti_csv
        ):
            ok_oggetti, msg_oggetti = oggetti.esporta_oggetti_csv()

        self.assertTrue(ok_segnalazioni, msg_segnalazioni)
        self.assertTrue(ok_oggetti, msg_oggetti)
        with segnalazioni_csv.open(encoding="utf-8", newline="") as file:
            self.assertEqual(
                next(csv.reader(file)),
                [
                    "id",
                    "titolo",
                    "descrizione",
                    "categoria",
                    "zona",
                    "priorita",
                    "data",
                    "stato",
                ],
            )
        with oggetti_csv.open(encoding="utf-8", newline="") as file:
            self.assertEqual(
                next(csv.reader(file)),
                [
                    "id",
                    "nome",
                    "descrizione",
                    "tipologia",
                    "luogo",
                    "annuncio",
                    "data",
                    "stato",
                ],
            )

    def test_round_trip_json_con_caratteri_accentati(self):
        dati = [{"titolo": "Città", "descrizione": "È già risolto"}]

        self.assertTrue(gestione_file.salva_json(self.segnalazioni_file, dati))
        self.assertEqual(gestione_file.carica_json(self.segnalazioni_file), dati)
        self.assertIn(
            "Città", self.segnalazioni_file.read_text(encoding="utf-8")
        )

    def test_caricamento_json_corrotto(self):
        self.segnalazioni_file.write_text("{ JSON non valido", encoding="utf-8")

        self.assertEqual(gestione_file.carica_json(self.segnalazioni_file), [])

    def test_caricamento_json_mancante(self):
        self.assertEqual(gestione_file.carica_json(self.segnalazioni_file), [])


if __name__ == "__main__":
    unittest.main()
