import datetime
import smtplib
from email.message import EmailMessage

import altair as alt
import pandas as pd
import streamlit as st

from database import criar_tabela, inserir_ticket, buscar_todos_os_tickets

# Função para envio de e-mail
def enviar_email_ticket(destinatario, nome, setor, problema, prioridade, ticket_id):
    EMAIL_REMETENTE = st.secrets["email"]["remetente"]
    SENHA_EMAIL = st.secrets["email"]["senha"]

    msg = EmailMessage()
    msg["Subject"] = f"Novo Ticket Aberto: {ticket_id}"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = ", ".join(destinatario)

    corpo = f"""
    Novo ticket foi aberto no sistema de suporte:

    🆔 ID: {ticket_id}
    🪪 Nome: {nome}
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

# Inicializa banco e dados
criar_tabela()
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(buscar_todos_os_tickets())

# Streamlit config
st.set_page_config(page_title="Suporte Plenitude", page_icon="🎫")
st.title("🎫 Suporte Plenitude")

st.write("""
Aplicativo interno da Plenitude Distribuidora para solicitação de 
Tickets de suporte de TI, assim podemos ter maior controle e 
disponibilidade com as solicitações!
""")

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
    hoje = datetime.datetime.now().date()
    ticket_id = f"TICKET-{hoje.strftime('%Y%m%d%H%')}"

    inserir_ticket(ticket_id, Nome, Setor, Problema, "Aberto", Prioridade, hoje)
    st.success("✅ Ticket Enviado com Sucesso!")

    # Atualiza os dados do banco na sessão
    st.session_state.df = buscar_todos_os_tickets()

    # Exibe o ticket
    novo_ticket = pd.DataFrame([{
        "ID": ticket_id,
        "Nome": Nome,
        "Setor": Setor,
        "Problema": Problema,
        "Status": "Aberto",
        "Prioridade": Prioridade,
        "Data de envio": hoje
    }])
    st.dataframe(novo_ticket, use_container_width=True, hide_index=True)

    # Envia e-mail
    enviar_email_ticket(
        destinatario=["joao.victor@plenitudedistribuidora.com.br", "bruno@plenitudedistribuidora.com.br"],
        nome=Nome,
        setor=Setor,
        problema=Problema,
        prioridade=Prioridade,
        ticket_id=ticket_id,
    )

# Exibição dos tickets existentes
st.header("Tickets Existentes")
st.write(f"Number of tickets: `{len(st.session_state.df)}`")

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
            options=["Alta", "Média", "Baixa"],
            required=True,
        ),
    },
    disabled=["ID", "Data de envio", "Nome"],
)

# Gráficos
st.header("Estatísticas")

col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Aberto"])
col1.metric(label="Número de tickets abertos", value=num_open_tickets)
col2.metric(label="Primeiro tempo de resposta (horas)", value=5.2)
col3.metric(label="Tempo médio de resolução (horas)", value=16)

st.write("##### Status do ticket por mês")
status_plot = (
    alt.Chart(st.session_state.df)
    .mark_bar()
    .encode(
        x="month(Data de envio):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
)
st.altair_chart(status_plot, use_container_width=True)

st.write("##### Prioridades atuais dos tickets")
priority_plot = (
    alt.Chart(st.session_state.df)
    .mark_arc()
    .encode(theta="count():Q", color="Prioridade:N")
    .properties(height=300)
)
st.altair_chart(priority_plot, use_container_width=True)