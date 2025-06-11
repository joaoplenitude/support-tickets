# app.py
import datetime
import pandas as pd
import streamlit as st
from database import criar_banco, inserir_ticket, carregar_tickets, atualizar_tickets
from email.message import EmailMessage
import smtplib


# Função para envio de e-mail
def enviar_email_ticket(destinatario, nome, setor, problema, prioridade, ticket_id):
    EMAIL_REMETENTE = st.secrets["email"]["remetente"]
    SENHA_EMAIL = st.secrets["email"]["senha"]

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
        with smtplib.SMTP_SSL("email-ssl.com.br", 465) as smtp:
            smtp.login(EMAIL_REMETENTE, SENHA_EMAIL)
            smtp.send_message(msg)
        st.success("📧 Notificação por e-mail enviada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")


# Config inicial
criar_banco()
st.set_page_config(page_title="Suporte Plenitude", page_icon="🌻")
st.title("🎫 Suporte Plenitude")

st.write(
    """
Aplicativo interno da Plenitude Distribuidora para solicitação de 
Tickets de suporte de TI, com maior controle e disponibilidade.
"""
)

# Carregar tickets do banco
if "df" not in st.session_state:
    st.session_state.df = carregar_tickets()

# Formulário de novo ticket
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
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    inserir_ticket(Nome, Setor, Problema, "Aberto", Prioridade, hoje)
    st.session_state.df = carregar_tickets()
    novo_id = st.session_state.df.iloc[0]["id"]

    st.success("✅ Ticket Enviado com Sucesso!")
    st.dataframe(st.session_state.df.head(1), use_container_width=True, hide_index=True)

    # Envio de e-mail
    def enviar_email_ticket(destinatario, nome, setor, problema, prioridade, ticket_id):
        EMAIL_REMETENTE = st.secrets["email"]["remetente"]
        SENHA_EMAIL = st.secrets["email"]["senha"]

        msg = EmailMessage()
        msg["Subject"] = f"Novo Ticket Aberto: TICKET-{ticket_id}"
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = ", ".join(destinatario)
        msg.set_content(
            f"""
        Novo ticket aberto:

        🆔 ID: TICKET-{ticket_id}
        👤 Nome: {nome}
        🏢 Setor: {setor}
        📋 Problema: {problema}
        🚨 Prioridade: {prioridade}
        """
        )

        try:
            with smtplib.SMTP_SSL("email-ssl.com.br", 465) as smtp:
                smtp.login(EMAIL_REMETENTE, SENHA_EMAIL)
                smtp.send_message(msg)
            st.success("📧 Notificação por e-mail enviada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao enviar e-mail: {e}")

    enviar_email_ticket(
        destinatario=[
            "joao.victor@plenitudedistribuidora.com.br",
            "bruno@plenitudedistribuidora.com.br",
        ],
        nome=Nome,
        setor=Setor,
        problema=Problema,
        prioridade=Prioridade,
        ticket_id=novo_id,
    )

# Tabela e edição
st.header("Tickets Existentes")
st.write(f"Número de tickets: `{len(st.session_state.df)}`")
st.info("Você pode editar os tickets clicando duas vezes nas células.", icon="✍️")

edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "status": st.column_config.SelectboxColumn(
            "Status", options=["Aberto", "Em Progresso", "Fechado"], required=True
        ),
        "prioridade": st.column_config.SelectboxColumn(
            "Prioridade", options=["Alta", "Média", "Baixa"], required=True
        ),
    },
    disabled=["id", "data_envio", "nome"],
)

if not edited_df.equals(st.session_state.df):
    atualizar_tickets(edited_df)
    st.session_state.df = carregar_tickets()
    st.success("✅ Tickets atualizados com sucesso!")

    # Envia o e-mail
    enviar_email_ticket(
        destinatario=[
            "joao.victor@plenitudedistribuidora.com.br",
            "bruno@plenitudedistribuidora.com.br",
        ],
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
