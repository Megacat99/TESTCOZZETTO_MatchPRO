from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os

# 1. Configurazione Percorsi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aura_db.sqlite")

app = FastAPI()

# 2. Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 3. Modelli Dati
class PartitaIn(BaseModel):
    id_p: int; casa: str; ospite: str; orario: str; data: str; stadio: str

class GolIn(BaseModel):
    marcatore: str; minuto: int; squadra: str

# 4. Rotte API
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, 'index.html'))

@app.get("/partite")
async def get_all():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS partite (id INTEGER PRIMARY KEY, casa TEXT, ospite TEXT, orario TEXT, data TEXT, stadio TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS gol (id INTEGER PRIMARY KEY AUTOINCREMENT, partita_id INTEGER, marcatore TEXT, minuto INTEGER, squadra TEXT)")
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
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO gol (partita_id, marcatore, minuto, squadra) VALUES (?,?,?,?)", 
              (id_p, g.marcatore.upper(), g.minuto, g.squadra))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.post("/partite")
async def add_match(p: PartitaIn):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO partite (id, casa, ospite, orario, data, stadio) VALUES (?,?,?,?,?,?)", 
              (p.id_p, p.casa.upper(), p.ospite.upper(), p.orario, p.data, p.stadio.upper()))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.delete("/partite/{id}")
async def delete_match(id: int):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM gol WHERE partita_id = ?", (id,))
    c.execute("DELETE FROM partite WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}

@app.delete("/gol/{id}")
async def delete_goal(id: int):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM gol WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}

# 5. MONTA I FILE STATICI (CSS/JS)
# Importante: Questo deve essere l'ultimo comando del file.
# Fa sì che /static/style.css venga letto correttamente.
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os

# Definiamo la cartella principale in modo dinamico
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aura_db.sqlite")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class PartitaIn(BaseModel):
    id_p: int; casa: str; ospite: str; orario: str; data: str; stadio: str

class GolIn(BaseModel):
    marcatore: str; minuto: int; squadra: str

@app.get("/")
async def read_index():
    # Usiamo il percorso assoluto per l'HTML
    return FileResponse(os.path.join(BASE_DIR, 'index.html'))

@app.get("/partite")
async def get_all():
    conn = sqlite3.connect(DB_NAME); conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS partite (id INTEGER PRIMARY KEY, casa TEXT, ospite TEXT, orario TEXT, data TEXT, stadio TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS gol (id INTEGER PRIMARY KEY AUTOINCREMENT, partita_id INTEGER, marcatore TEXT, minuto INTEGER, squadra TEXT)")
    c.execute("SELECT * FROM partite ORDER BY data DESC")
    partite = [dict(row) for row in c.fetchall()]
    for p in partite:
        c.execute("SELECT * FROM gol WHERE partita_id = ? ORDER BY minuto ASC", (p['id'],))
        p['gol'] = [dict(g) for g in c.fetchall()]
        p['score_casa'] = sum(1 for g in p['gol'] if g['squadra'] == 'casa')
        p['score_ospite'] = sum(1 for g in p['gol'] if g['squadra'] == 'ospite')
    conn.close()
    return partite

# ... rotte POST e DELETE (mantienile come le hai ora) ...
@app.post("/partite/{id_p}/gol")
async def add_goal(id_p: int, g: GolIn):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO gol (partita_id, marcatore, minuto, squadra) VALUES (?,?,?,?)", (id_p, g.marcatore.upper(), g.minuto, g.squadra))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.post("/partite")
async def add_match(p: PartitaIn):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO partite (id, casa, ospite, orario, data, stadio) VALUES (?,?,?,?,?,?)", (p.id_p, p.casa.upper(), p.ospite.upper(), p.orario, p.data, p.stadio.upper()))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.delete("/partite/{id}")
async def delete_match(id: int):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM gol WHERE partita_id = ?", (id,)); c.execute("DELETE FROM partite WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}

@app.delete("/gol/{id}")
async def delete_goal(id: int):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM gol WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}

# LA RIGA FONDAMENTALE: Monta la cartella corrente come "/static"
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os

# Configurazione percorsi assoluti per Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aura_db.sqlite")

app = FastAPI()

# Middleware CORS per permettere al tuo HTML di comunicare con il Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class PartitaIn(BaseModel):
    id_p: int; casa: str; ospite: str; orario: str; data: str; stadio: str

class GolIn(BaseModel):
    marcatore: str; minuto: int; squadra: str

@app.get("/")
async def read_index():
    # Serve il tuo file index.html originale
    return FileResponse(os.path.join(BASE_DIR, 'index.html'))

@app.get("/partite")
async def get_all():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Crea tabelle se non esistono (per sicurezza al primo avvio)
    c.execute("CREATE TABLE IF NOT EXISTS partite (id INTEGER PRIMARY KEY, casa TEXT, ospite TEXT, orario TEXT, data TEXT, stadio TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS gol (id INTEGER PRIMARY KEY AUTOINCREMENT, partita_id INTEGER, marcatore TEXT, minuto INTEGER, squadra TEXT)")

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
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO gol (partita_id, marcatore, minuto, squadra) VALUES (?,?,?,?)",
              (id_p, g.marcatore.upper(), g.minuto, g.squadra))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.post("/partite")
async def add_match(p: PartitaIn):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO partite (id, casa, ospite, orario, data, stadio) VALUES (?,?,?,?,?,?)",
              (p.id_p, p.casa.upper(), p.ospite.upper(), p.orario, p.data, p.stadio.upper()))
    conn.commit(); conn.close()
    return {"status": "success"}

@app.delete("/partite/{id}")
async def delete_match(id: int):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM gol WHERE partita_id = ?", (id,))
    c.execute("DELETE FROM partite WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}

@app.delete("/gol/{id}")
async def delete_goal(id: int):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM gol WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}

# Monta la cartella static dove tieni il file style.css
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
