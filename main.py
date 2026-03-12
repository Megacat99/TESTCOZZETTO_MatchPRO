from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os
from pathlib import Path

# Percorsi
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "aura_db.sqlite")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Modelli
class PartitaIn(BaseModel):
    id_p: int; casa: str; ospite: str; orario: str; data: str; stadio: str
class GolIn(BaseModel):
    marcatore: str; minuto: int; squadra: str

# Database
@app.on_event("startup")
def setup_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS partite (id INTEGER PRIMARY KEY, casa TEXT, ospite TEXT, orario TEXT, data TEXT, stadio TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS gol (id INTEGER PRIMARY KEY AUTOINCREMENT, partita_id INTEGER, marcatore TEXT, minuto INTEGER, squadra TEXT, FOREIGN KEY(partita_id) REFERENCES partite(id))")
    conn.commit()
    conn.close()

# --- GESTIONE FILE STATICI (TUTTO NELLA ROOT) ---

# Questa riga dice: "Quando il browser chiede /static/..., cercalo direttamente nella root"
app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")

@app.get("/")
async def read_index():
    # Invia il file index.html che si trova nella root
    return FileResponse(str(BASE_DIR / 'index.html'))

# --- ENDPOINT API (Invariati) ---

@app.get("/partite")
async def get_all():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; c = conn.cursor()
    c.execute("SELECT * FROM partite ORDER BY data DESC")
    partite = [dict(row) for row in c.fetchall()]
    for p in partite:
        c.execute("SELECT * FROM gol WHERE partita_id = ? ORDER BY minuto ASC", (p['id'],))
        p['gol'] = [dict(g) for g in c.fetchall()]
        p['score_casa'] = sum(1 for g in p['gol'] if g['squadra'] == 'casa')
        p['score_ospite'] = sum(1 for g in p['gol'] if g['squadra'] == 'ospite')
    conn.close()
    return partite

@app.post("/partite")
async def add_match(p: PartitaIn):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO partite VALUES (?,?,?,?,?,?)", (p.id_p, p.casa.upper(), p.ospite.upper(), p.orario, p.data, p.stadio.upper()))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.post("/partite/{id_p}/gol")
async def add_goal(id_p: int, g: GolIn):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT INTO gol (partita_id, marcatore, minuto, squadra) VALUES (?,?,?,?)", (id_p, g.marcatore.upper(), g.minuto, g.squadra))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.delete("/partite/{id}")
async def delete_match(id: int):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("DELETE FROM gol WHERE partita_id = ?", (id,))
    c.execute("DELETE FROM partite WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}

@app.delete("/gol/{id}")
async def delete_goal(id: int):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("DELETE FROM gol WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}
