from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os
from pathlib import Path

# Definiamo i percorsi in modo robusto
BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "aura_db.sqlite"

app = FastAPI()

# Configurazione CORS per evitare blocchi del browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class PartitaIn(BaseModel):
    id_p: int
    casa: str
    ospite: str
    orario: str
    data: str
    stadio: str

class GolIn(BaseModel):
    marcatore: str
    minuto: int
    squadra: str

# Inizializzazione del Database all'avvio dell'app
@app.on_event("startup")
def setup_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabella Partite
    c.execute("""
        CREATE TABLE IF NOT EXISTS partite (
            id INTEGER PRIMARY KEY, 
            casa TEXT, 
            ospite TEXT, 
            orario TEXT, 
            data TEXT, 
            stadio TEXT
        )
    """)
    # Tabella Gol
    c.execute("""
        CREATE TABLE IF NOT EXISTS gol (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            partita_id INTEGER, 
            marcatore TEXT, 
            minuto INTEGER, 
            squadra TEXT,
            FOREIGN KEY(partita_id) REFERENCES partite(id)
        )
    """)
    conn.commit()
    conn.close()

@app.get("/")
async def read_index():
    return FileResponse(BASE_DIR / 'index.html')

@app.get("/partite")
async def get_all():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM partite ORDER BY data DESC")
    partite = [dict(row) for row in c.fetchall()]
    for p in partite:
        c.execute("SELECT * FROM gol WHERE partita_id = ? ORDER BY minuto ASC", (p['id'],))
        p['gol'] = [dict(g) for g in c.fetchall()]
        p['score_casa'] = sum(1 for g in p['gol'] if g['squadra'] == 'casa')
        p['score_ospite'] = sum(1 for g in p['gol'] if g['squadra'] == 'ospite')
    conn.close()
    return partite

@app.post("/partite/{id_p}/gol")
async def add_goal(id_p: int, g: GolIn):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO gol (partita_id, marcatore, minuto, squadra) VALUES (?,?,?,?)", 
              (id_p, g.marcatore.upper(), g.minuto, g.squadra))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/partite")
async def add_match(p: PartitaIn):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO partite (id, casa, ospite, orario, data, stadio) VALUES (?,?,?,?,?,?)", 
              (p.id_p, p.casa.upper(), p.ospite.upper(), p.orario, p.data, p.stadio.upper()))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.delete("/partite/{id}")
async def delete_match(id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM gol WHERE partita_id = ?", (id,))
    c.execute("DELETE FROM partite WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@app.delete("/gol/{id}")
async def delete_goal(id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM gol WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

# Importante: montiamo i file statici per caricare style.css
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
