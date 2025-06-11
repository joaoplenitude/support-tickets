# database.py
import sqlite3

def criar_banco():
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            setor TEXT NOT NULL,
            problema TEXT NOT NULL,
            status TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            data_envio TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def inserir_ticket(nome, setor, problema, status, prioridade, data_envio):
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO tickets (nome, setor, problema, status, prioridade, data_envio)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, setor, problema, status, prioridade, data_envio))
    conn.commit()
    conn.close()

def carregar_tickets():
    conn = sqlite3.connect("tickets.db")
    df = pd.read_sql_query("SELECT * FROM tickets ORDER BY id DESC", conn)
    conn.close()
    return df

def atualizar_tickets(df):
    conn = sqlite3.connect("tickets.db")
    df.to_sql("tickets", conn, if_exists="replace", index=False)
    conn.close()
