# ⚽ MatchPRO.IO PROGETTO COZZETTO

MatchPRO.IO è una piattaforma di gestione e analisi delle partite di calcio con un'interfaccia futuristica in stile Cyberpunk/Neon. Il sistema permette di registrare partite, marcatore per marcatore, fornendo statistiche in tempo reale e grafici interattivi.

# 🚀 Caratteristiche Principali

    Gestione Match: Inserimento, modifica ed eliminazione di partite con dettagli su stadio, data e orario.

    Tracking Gol: Registrazione dinamica dei marcatori (casa/ospite) con validazione del tempo di gioco (fino a 120').

    Dashboard Statistica: Visualizzazione automatica della classifica squadre e dei top marcatori.

    Data Visualization: Grafici a torta alimentati da Chart.js per analizzare la distribuzione dei gol.

    Design Reattivo: Supporto nativo per Dark Mode e Light Mode con estetica ad alto contrasto.

# Backend

    Python 3.x

    FastAPI: Framework web ad alte prestazioni per le API.

    SQLite3: Database relazionale leggero per la persistenza dei dati.

    Pydantic: Validazione dei dati tramite schemi definiti.

# Frontend

    HTML5 / CSS3: Layout a griglia con variabili CSS dinamiche.

    JavaScript (Vanilla): Gestione asincrona delle chiamate API tramite fetch.

    Chart.js: Libreria per la visualizzazione dei dati statistici. (è uno script dentro l'html)

# 📦 Installazione e Utilizzo
1. Prerequisiti

Assicurati di avere Python installato sul tuo sistema.

2. Configurazione Ambiente

Clona la repository e installa le dipendenze necessarie:

pip install -r requirements.txt

Le dipendenze principali includono fastapi, uvicorn, e pydantic.

3. Avvio del Server

Per avviare il backend e rendere l'interfaccia accessibile sulla tua rete locale:

uvicorn main:app --reload

4. Accesso al Sito

Una volta avviato il server, apri il browser all'indirizzo:
http://127.0.0.1:8000/

# 📂 Struttura dei File

    main.py: Punto di ingresso del server FastAPI, contiene tutta la logica API e la gestione del database.

    aura_db.sqlite: Database SQLite contenente le tabelle partite e gol.

    index.html: L'interfaccia utente principale dell'applicazione.

    style.css: Foglio di stile con definizioni per i temi Dark e Light.

    requirements.txt: Elenco delle librerie Python richieste.

# 📊 Database Schema

L'applicazione utilizza due tabelle principali:

    partite: id, casa, ospite, orario, data, stadio.

    gol: id, partita_id (FK), marcatore, minuto, squadra.
