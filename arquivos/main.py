
import streamlit as st

st.set_page_config(page_title="Fornecedor 2ºA", layout="wide")

# Menu lateral
menu = st.sidebar.radio("📂 Navegação", ["🛒 Página de Compras", "📊 Dashboard de Vendas"])

if menu == "🛒 Página de Compras":
    import compras
elif menu == "📊 Dashboard de Vendas":
    import dashboard
