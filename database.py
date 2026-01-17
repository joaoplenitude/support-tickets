# database.py
import sqlite3

def criar_tabela():
    conn = sqlite3.connect("ticket.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            Nome TEXT NOT NULL,
            Setor TEXT NOT NULL,
            Problema TEXT NOT NULL,
            Status TEXT NOT NULL,
            Prioridade TEXT NOT NULL,
            data_envio DATE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def inserir_ticket(ticket_id, nome, setor, problema, status, prioridade, data_envio):
    conn = sqlite3.connect("ticket.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (id, Nome, Setor, Problema, Status, Prioridade, data_envio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, nome, setor, problema, status, prioridade, data_envio))
    conn.commit()
    conn.close()

def buscar_todos_os_tickets():
    conn = sqlite3.connect("ticket.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    rows = cursor.fetchall()
    conn.close()
    return rows
