from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os

# 1. PERCORSO CORRETTO PER IL CLOUD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aura_db.sqlite")

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Definizione schemi
class PartitaIn(BaseModel):
    id_p: int; casa: str; ospite: str; orario: str; data: str; stadio: str

class GolIn(BaseModel):
    marcatore: str; minuto: int; squadra: str

# 2. CORRETTA INDENTAZIONE (deve stare fuori dalle classi)
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/partite")
async def get_all():
    conn = sqlite3.connect(DB_NAME); conn.row_factory = sqlite3.Row
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
    if not (1 <= g.minuto <= 120):
        raise HTTPException(status_code=400, detail="Minuto non valido")
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO gol (partita_id, marcatore, minuto, squadra) VALUES (?,?,?,?)", 
              (id_p, g.marcatore.upper(), g.minuto, g.squadra))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.delete("/gol/{id}")
async def delete_goal(id: int):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM gol WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}

@app.post("/partite")
async def add_match(p: PartitaIn):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO partite (id, casa, ospite, orario, data, stadio) 
                 VALUES (?,?,?,?,?,?)""", (p.id_p, p.casa.upper(), p.ospite.upper(), p.orario, p.data, p.stadio.upper()))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.delete("/partite/{id}")
async def delete_match(id: int):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM partite WHERE id = ?", (id,))
    c.execute("DELETE FROM gol WHERE partita_id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}
