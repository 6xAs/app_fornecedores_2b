
import streamlit as st
import pandas as pd

st.title("📊 Dashboard de Vendas - Fornecedor 2ºA")

# Caminho do CSV
vendas_path = "database/vendas/vendas.csv"

# Tentar carregar dados
try:
    df_vendas = pd.read_csv(vendas_path)
except FileNotFoundError:
    st.warning("Nenhuma venda registrada ainda.")
    df_vendas = pd.DataFrame()

if not df_vendas.empty:
    # Conversão de valores, caso necessário
    for col in ["Valor Total (R$)", "Encargo (R$)", "Valor Unitário (R$)"]:
        df_vendas[col] = pd.to_numeric(df_vendas[col], errors="coerce").fillna(0.0)

    total_vendas = df_vendas["Valor Total (R$)"].sum()
    total_encargos = df_vendas["Encargo (R$)"].sum()
    total_itens = df_vendas["Quantidade"].sum()
    lucro_liquido = total_vendas - total_encargos

    st.metric("🛍️ Total em Vendas (R$)", f"{total_vendas:,.2f}")
    st.metric("📉 Total de Encargos (R$)", f"{total_encargos:,.2f}")
    st.metric("📦 Quantidade Total Vendida", int(total_itens))
    st.metric("💰 Lucro Líquido Estimado (R$)", f"{lucro_liquido:,.2f}")

    st.markdown("### 📋 Detalhes das Vendas")
    st.dataframe(df_vendas)
else:
    st.info("Nenhuma venda registrada ainda.")
