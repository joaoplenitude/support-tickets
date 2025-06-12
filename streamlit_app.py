# streamlit_app.py
import datetime
import random
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
    🏬 Setor: {setor}
    📝 Problema: {problema}
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

dados = buscar_todos_os_tickets()
st.session_state.df = pd.DataFrame(dados, columns=[
    "ID", "Nome", "Setor", "Problema", "Status", "Prioridade", "Data de envio"
]) if "df" not in st.session_state else st.session_state.df

# Streamlit config
st.set_page_config(page_title="Suporte de TI Plenitude", page_icon="🎫")
st.title("👨‍💻| Suporte de TI Plenitude")

st.write("""
Este é o nosso canal oficial para abertura de tickets de suporte de TI. Por aqui, você pode registrar suas 
solicitações de forma prática e organizada, garantindo mais agilidade no atendimento, 
maior controle das demandas e melhor acompanhamento das soluções.
Conte conosco — estamos aqui para te ajudar!
""")

# Formulário para novo ticket
st.header("Adicionar um 🎫|Ticket")

with st.form("add_ticket_form"):
    Nome = st.text_area("Nome")
    Setor = st.selectbox(
        "Setor",
        [
            "Produção", "Comercial", "Marketplace", "RH",
            "Administrativo", "Marketing", "SAC",
        ],
    )
    Problema = st.text_area("Descreva o seu problema")
    Prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
    submitted = st.form_submit_button("Enviar")

if submitted:
    if not Nome.strip() or not Problema.strip():
        st.warning("Por favor, preencha todos os campos obrigatórios.")
    else:
        hoje = datetime.datetime.now()
        ticket_id = f"TICKET-{hoje.strftime('%Y%m%d%H%M%S')}-{random.randint(100,999)}"

        inserir_ticket(ticket_id, Nome, Setor, Problema, "Aberto", Prioridade, hoje.date())
        st.success("✅ Ticket Enviado com Sucesso!")

        dados_atualizados = buscar_todos_os_tickets()
        st.session_state.df = pd.DataFrame(dados_atualizados, columns=[
            "ID", "Nome", "Setor", "Problema", "Status", "Prioridade", "Data de envio"
        ])

        novo_ticket = pd.DataFrame([{
            "ID": ticket_id,
            "Nome": Nome,
            "Setor": Setor,
            "Problema": Problema,
            "Status": "Aberto",
            "Prioridade": Prioridade,
            "Data de envio": hoje.date()
        }])
        st.dataframe(novo_ticket, use_container_width=True, hide_index=True)

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
            "Status", help="Ticket status",
            options=["Aberto", "Em Progresso", "Fechado"], required=True,
        ),
        "Prioridade": st.column_config.SelectboxColumn(
            "Prioridade", help="Prioridade",
            options=["Alta", "Média", "Baixa"], required=True,
        ),
    },
    disabled=["ID", "Setor", "Data de envio", "Nome"]
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
    .configure_axis(labelFontSize=12, titleFontSize=14)
    .configure_legend(orient="bottom", titleFontSize=13, labelFontSize=12)
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
