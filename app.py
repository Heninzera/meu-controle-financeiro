import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# Configuração da página (Nome na aba, ícone e layout para celular)
st.set_page_config(page_title="Meu Controle", page_icon="📱", layout="centered")

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
SUPABASE_URL = "https://ejlfobprtuvtxjhrecgw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVqbGZvYnBydHV2dHhqaHJlY2d3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1OTUxMjYsImV4cCI6MjA4OTE3MTEyNn0.0-9krcpcFX4FaeUDhdBajAuqoBZ-RwqtdpzMbtNk_PQ"
URL_TABELA = f"{SUPABASE_URL}/rest/v1/lancamentos"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.title("💸 Meu Controle Financeiro")

# Criando as Abas do Aplicativo
aba_lancamento, aba_dashboard = st.tabs(["📝 Lançar", "📊 Dashboard"])

# --- ABA 1: LANÇAMENTOS ---
with aba_lancamento:
    st.subheader("Novo Registro")
    
    # Categorias com Ícones
    receitas_lista = ["💼 Salário", "🍔 iFood", "🚗 99", "➕ Outras Receitas"]
    despesas_lista = ["📱 Celular", "🏍️ CB 300", "⛽ Gasolina", "💳 Cartão de Crédito", "🌐 Internet", "➖ Outras Despesas"]

    col1, col2 = st.columns(2)

    with col1:
        tipo = st.radio("Tipo", ["Receita", "Despesa"])
        data_lancamento = st.date_input("Data", datetime.today())

    with col2:
        if tipo == "Receita":
            categoria = st.selectbox("Categoria", receitas_lista)
        else:
            categoria = st.selectbox("Categoria", despesas_lista)
            
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

    if st.button("💾 Salvar Lançamento", use_container_width=True):
        novo_dado = {
            "data": data_lancamento.isoformat(),
            "tipo": tipo,
            "categoria": categoria,
            "valor": valor
        }
        
        resposta = requests.post(URL_TABELA, headers=HEADERS, json=novo_dado)
        
        if resposta.status_code == 201:
            st.success(f"✅ Salvo! {categoria}: R$ {valor}")
            st.rerun()
        else:
            st.error("Erro ao salvar no banco de dados.")

# --- ABA 2: DASHBOARD E GRÁFICOS ---
with aba_dashboard:
    resposta_get = requests.get(f"{URL_TABELA}?select=*", headers=HEADERS)

    if resposta_get.status_code == 200:
        dados_nuvem = resposta_get.json()
        
        if len(dados_nuvem) > 0:
            df = pd.DataFrame(dados_nuvem)
            
            # Cálculos Principais
            total_receitas = df[df['tipo'] == 'Receita']['valor'].sum()
            total_despesas = df[df['tipo'] == 'Despesa']['valor'].sum()
            saldo_atual = total_receitas - total_despesas

            # Cartões de Resumo Bonitos
            col_saldo, col_rec, col_desp = st.columns(3)
            col_saldo.metric("Saldo Atual", f"R$ {saldo_atual:.2f}")
            col_rec.metric("Receitas", f"R$ {total_receitas:.2f}")
            col_desp.metric("Despesas", f"R$ {total_despesas:.2f}")
            
            st.divider()

            # Prepara os dados para os gráficos
            df['data'] = pd.to_datetime(df['data'])
            
            # --- Gráfico 1: Para onde está indo o dinheiro? (Gráfico de Rosca) ---
            st.subheader("Para onde vai o dinheiro?")
            df_despesas = df[df['tipo'] == 'Despesa']
            if not df_despesas.empty:
                grafico_pizza = px.pie(
                    df_despesas, 
                    values='valor', 
                    names='categoria', 
                    hole=0.4, # Deixa o meio furado (rosca)
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                st.plotly_chart(grafico_pizza, use_container_width=True)
            else:
                st.info("Nenhuma despesa registrada ainda.")

            # --- Tabela de Histórico ---
            st.subheader("Histórico Completo")
            df_mostrar = df[['data', 'tipo', 'categoria', 'valor']].copy()
            df_mostrar['data'] = df_mostrar['data'].dt.strftime('%d/%m/%Y')
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

        else:
            st.info("Nenhum lançamento encontrado. Faça seu primeiro registro na aba 'Lançar'!")
