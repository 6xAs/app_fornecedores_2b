
import streamlit as st
import pandas as pd
from datetime import datetime

# Caminhos dos arquivos
produtos_path = "database/produtos/produtos.csv"
vendas_path = "database/vendas/vendas.csv"

# Carregar dados
df_produtos = pd.read_csv(produtos_path)
df_vendas = pd.read_csv(vendas_path)

st.title("🛒 Sistema de Vendas - Fornecedor 2ºA")

# Seleção de produto
produto_selecionado = st.selectbox("Selecione um produto", df_produtos["Nome do Produto"].unique())
produto_info = df_produtos[df_produtos["Nome do Produto"] == produto_selecionado].iloc[0]

# Exibir informações
st.subheader("📦 Informações do Produto")
st.write(f"**Categoria:** {produto_info['Categoria']}")
st.write(f"**Estoque Disponível:** {produto_info['Estoque Disponível']}")
st.write(f"**Preço Unitário (R$):** {produto_info['Preço Unitário (R$)']}")
st.write(f"**Total de Impostos:** {produto_info['Total de Impostos (%)']}%")
st.write(f"**Preço Final com Impostos (R$):** {produto_info['Preço Final c/ Impostos (R$)']}")

# Quantidade e dados do comprador
quantidade = st.number_input("Quantidade", min_value=1, max_value=int(produto_info["Estoque Disponível"]), step=1)
nome = st.text_input("Nome do Comprador")
empresa = st.text_input("Empresa / Equipe")
email = st.text_input("Email")
encargo_percentual = 0.20  # fixo

# Cálculo de valores
valor_unitario = produto_info["Preço Final c/ Impostos (R$)"]
valor_total = valor_unitario * quantidade
encargo_valor = valor_total * encargo_percentual

if st.button("💾 Finalizar Pedido"):
    nova_venda = {
        "Data da Compra": datetime.today().strftime('%Y-%m-%d'),
        "Nome do Comprador": nome,
        "Empresa": empresa,
        "Email": email,
        "Produto": produto_selecionado,
        "Categoria": produto_info["Categoria"],
        "Quantidade": quantidade,
        "Valor Unitário (R$)": valor_unitario,
        "Valor Total (R$)": valor_total,
        "Encargo (%)": encargo_percentual * 100,
        "Encargo (R$)": encargo_valor
    }

    df_vendas = pd.concat([df_vendas, pd.DataFrame([nova_venda])], ignore_index=True)
    df_vendas.to_csv(vendas_path, index=False)
    st.success("✅ Pedido registrado com sucesso!")

st.markdown("---")
st.subheader("📊 Dashboard de Vendas")

if not df_vendas.empty:
    total_vendas = df_vendas["Valor Total (R$)"].sum()
    total_encargos = df_vendas["Encargo (R$)"].sum()
    total_itens = df_vendas["Quantidade"].sum()
    lucro_liquido = total_vendas - total_encargos

    st.metric("🛍️ Total em Vendas (R$)", f"{total_vendas:,.2f}")
    st.metric("📉 Total de Encargos (R$)", f"{total_encargos:,.2f}")
    st.metric("📦 Quantidade Total Vendida", int(total_itens))
    st.metric("💰 Lucro Líquido Estimado (R$)", f"{lucro_liquido:,.2f}")
    st.dataframe(df_vendas)
else:
    st.info("Nenhuma venda registrada ainda.")
