import sqlite3
from datetime import datetime
import pandas as pd

DB_FILE = "tickets.db"

# Cria o banco de dados e a tabela, se não existir
def criar_banco():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE,
            nome TEXT,
            setor TEXT,
            problema TEXT,
            status TEXT,
            prioridade TEXT,
            data_envio TEXT
        )
    """)
    conn.commit()
    conn.close()

# Insere um novo ticket no banco de dados
def inserir_ticket(ticket_id, nome, setor, problema, status, prioridade, data_envio):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (ticket_id, nome, setor, problema, status, prioridade, data_envio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, nome, setor, problema, status, prioridade, data_envio))
    conn.commit()
    conn.close()

# Retorna todos os tickets como um DataFrame
def carregar_tickets():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM tickets ORDER BY id DESC", conn)
    conn.close()
    return df

# Atualiza os tickets (espera receber um DataFrame editado)
def atualizar_todos_tickets(df_editado):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for _, row in df_editado.iterrows():
        cursor.execute("""
            UPDATE tickets
            SET status = ?, prioridade = ?
            WHERE ticket_id = ?
        """, (row["Status"], row["Prioridade"], row["ID"]))
    conn.commit()
    conn.close()

# Pega o último número de ticket para continuar incrementando
def ultimo_numero_ticket():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM tickets")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0
