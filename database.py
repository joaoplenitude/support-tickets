import sqlite3


# Conecta ao banco de dados (cria se não existir)
def conectar():
    return sqlite3.connect("ticket.db", check_same_thread=False)


# Cria a tabela de tickets
def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            nome TEXT,
            setor TEXT,
            problema TEXT,
            status TEXT,
            prioridade TEXT,
            data_envio TEXT
        )
    """
    )
    conn.commit()
    conn.close()


# Insere um novo ticket
def inserir_ticket(ticket_id, nome, setor, problema, status, prioridade, data_envio):
    conn = sqlite3.connect("ticket.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tickets (id, Nome, Setor, Problema, Status, Prioridade, Data_envio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (ticket_id, nome, setor, problema, status, prioridade, data_envio),
    )
    conn.commit()
    conn.close()


# Busca todos os tickets
def buscar_todos_os_tickets():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    rows = cursor.fetchall()
    conn.close()

    tickets = []
    for row in rows:
        tickets.append(
            {
                "ID": row[0],
                "Nome": row[1],
                "Setor": row[2],
                "Problema": row[3],
                "Status": row[4],
                "Prioridade": row[5],
                "Data de envio": row[6],
            }
        )
    return tickets
