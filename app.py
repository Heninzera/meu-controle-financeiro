import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# Cole suas chaves dentro das aspas abaixo
SUPABASE_URL = "https://ejlfobprtuvtxjhrecgw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVqbGZvYnBydHV2dHhqaHJlY2d3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1OTUxMjYsImV4cCI6MjA4OTE3MTEyNn0.0-9krcpcFX4FaeUDhdBajAuqoBZ-RwqtdpzMbtNk_PQ"

# Monta o endereço exato da sua tabela
URL_TABELA = f"{SUPABASE_URL}/rest/v1/lancamentos"

# Cabeçalhos de segurança que o Supabase exige
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.title("Controle Financeiro Diário")

receitas_lista = ["SALARIO", "IFOOD", "99", "OUTROS_RECEITA"]
despesas_lista = ["CELULAR", "CB 300", "GASOLINA", "CARTAO", "INTERNET", "OUTROS_DESPESA"]

st.subheader("Novo Lançamento")

col1, col2 = st.columns(2)

with col1:
    tipo = st.radio("Tipo de Lançamento", ["Receita", "Despesa"])
    data_lancamento = st.date_input("Data", datetime.today())

with col2:
    if tipo == "Receita":
        categoria = st.selectbox("Categoria", receitas_lista)
    else:
        categoria = st.selectbox("Categoria", despesas_lista)
        
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

if st.button("Salvar Lançamento"):
    novo_dado = {
        "data": data_lancamento.isoformat(),
        "tipo": tipo,
        "categoria": categoria,
        "valor": valor
    }
    
    # Envia o dado direto para a API do Supabase
    resposta = requests.post(URL_TABELA, headers=HEADERS, json=novo_dado)
    
    if resposta.status_code == 201:
        st.success(f"Lançamento salvo na nuvem! {categoria}: R$ {valor}")
        st.rerun()
    else:
        st.error(f"Erro ao salvar: {resposta.text}")

st.divider()

# --- BUSCANDO DADOS DA NUVEM ---
# Pede todos os dados para a API
resposta_get = requests.get(f"{URL_TABELA}?select=*", headers=HEADERS)

if resposta_get.status_code == 200:
    dados_nuvem = resposta_get.json()
    
    if len(dados_nuvem) > 0:
        df = pd.DataFrame(dados_nuvem)
        
        total_receitas = df[df['tipo'] == 'Receita']['valor'].sum()
        total_despesas = df[df['tipo'] == 'Despesa']['valor'].sum()
        saldo_atual = total_receitas - total_despesas

        st.metric(label="Saldo Total", value=f"R$ {saldo_atual:.2f}")

        df_mostrar = df[['data', 'tipo', 'categoria', 'valor']].copy()
        
        # Converte a coluna data para o formato BR
        df_mostrar['data'] = pd.to_datetime(df_mostrar['data']).dt.strftime('%d/%m/%Y')
        
        st.subheader("Histórico de Lançamentos (Nuvem)")
        st.dataframe(df_mostrar, use_container_width=True)
    else:
        st.metric(label="Saldo Total", value="R$ 0.00")
        st.info("Nenhum lançamento encontrado. Faça seu primeiro registro acima!")
else:
    st.error("Não foi possível conectar ao banco de dados.")