import datetime
import random
import smtplib
from email.message import EmailMessage

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


# Função para envio de e-mail
def enviar_email_ticket(destinatario, nome, setor, problema, prioridade, ticket_id):
    EMAIL_REMETENTE = "SEU_EMAIL@gmail.com"
    SENHA_EMAIL = "SENHA_DO_EMAIL"

    msg = EmailMessage()
    msg["Subject"] = f"Novo Ticket Aberto: {ticket_id}"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destinatario

    corpo = f"""
    Novo ticket foi aberto no sistema de suporte:

    🆔 ID: {ticket_id}
    👤 Nome: {nome}
    🏢 Setor: {setor}
    📋 Problema: {problema}
    🚨 Prioridade: {prioridade}

    Verifique o sistema para mais detalhes.
    """
    msg.set_content(corpo)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_REMETENTE, SENHA_EMAIL)
            smtp.send_message(msg)
        st.success("📧 Notificação por e-mail enviada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")


# Streamlit config
st.set_page_config(page_title="Suporte Plenitude", page_icon="🎫")
st.title("🎫 Suporte Plenitude")

st.write(
    """
Aplicativo interno da Plenitude Distribuidora para solicitação de 
Tickets de suporte de TI, assim podemos ter maior controle e 
disponibilidade com as solicitações!
"""
)

# Inicializa DataFrame se ainda não existe
if "df" not in st.session_state:
    np.random.seed(10)
    issue_descriptions = ["Problema de exemplo"]
    data = {
        "ID": [f"TICKET-{i}" for i in range(1, 3)],
        "Nome": np.random.choice(["Marcelo", "Ricardo", "Renan"], size=2),
        "Setor": np.random.choice(["Comercial", "RH", "Produção"], size=2),
        "Problema": np.random.choice(issue_descriptions, size=2),
        "Status": np.random.choice(["Aberto", "Em Progresso", "Fechado"], size=2),
        "Prioridade": np.random.choice(["Alta", "Média", "Baixa"], size=2),
        "Data de envio": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(2)
        ],
    }
    st.session_state.df = pd.DataFrame(data)

# Formulário para novo ticket
st.header("Adicionar um 🎫|Ticket")

with st.form("add_ticket_form"):
    Nome = st.text_area("Nome")
    Setor = st.selectbox(
        "Setor",
        [
            "Produção",
            "Comercial",
            "Marketplace",
            "RH",
            "Administrativo",
            "Marketing",
            "SAC",
        ],
    )
    Problema = st.text_area("Descreva o seu problema")
    Prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
    submitted = st.form_submit_button("Enviar")

if submitted:
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    hoje = datetime.datetime.now().date()

    novo_ticket = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number + 1}",
                "Nome": Nome,
                "Setor": Setor,
                "Problema": Problema,
                "Status": "Aberto",
                "Prioridade": Prioridade,
                "Data de envio": hoje,
            }
        ]
    )

    st.session_state.df = pd.concat([novo_ticket, st.session_state.df], axis=0)
    st.write("✅ Ticket Enviado com Sucesso!")
    st.dataframe(novo_ticket, use_container_width=True, hide_index=True)

    # Envia o e-mail
    enviar_email_ticket(
        destinatario="EMAIL_DESTINO@empresa.com",
        nome=Nome,
        setor=Setor,
        problema=Problema,
        prioridade=Prioridade,
        ticket_id=f"TICKET-{recent_ticket_number + 1}",
    )


# Show section to view and edit existing tickets in a table.
st.header("Tickets Existentes")
st.write(f"Number of tickets: `{len(st.session_state.df)}`")

st.info(
    "You can edit the tickets by double clicking on a cell. Note how the plots below "
    "update automatically! You can also sort the table by clicking on the column headers.",
    icon="✍️",
)

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket status",
            options=["Aberto", "Em Progresso", "Fechado"],
            required=True,
        ),
        "Prioridade": st.column_config.SelectboxColumn(
            "Prioridade",
            help="Prioridade",
            options=["Alto", "Médio", "Baixo"],
            required=True,
        ),
    },
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Data de envio", "Nome"],
)

# Show some metrics and charts about the ticket.
st.header("Statistics")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
col1.metric(label="Número de tickets abertos", value=num_open_tickets, delta=10)
col2.metric(label="Primeiro tempo de resposta (horas)", value=5.2, delta=-1.5)
col3.metric(label="Tempo médio de resolução (horas)", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### Status do ticket por mês")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Prioridades atuais dos tickets")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
