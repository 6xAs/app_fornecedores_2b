
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Caminhos dos arquivos
produtos_path = "database/produtos/produtos_completos_formatado.csv"
vendas_dir = "database/vendas"
os.makedirs(vendas_dir, exist_ok=True)

st.set_page_config(page_title="Fornecedor 2ºA", layout="wide")
st.title("🛒 Sistema de Compras - Fornecedores 2ºA 🟠")


# Estado do carrinho
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# Carregamento dos dados com tratamento
try:
    df_produtos = pd.read_csv(produtos_path)
    assert not df_produtos.empty, "Arquivo de produtos está vazio!"
except Exception as e:
    st.error(f"❌ Erro ao carregar produtos: {e}")
    st.stop()

# Função para formatar colunas monetárias
def formatar_coluna_monetaria(df, colunas):
    def ajustar_valor(valor):
        try:
            valor = float(valor)

            # Corrigir valores inflacionados (ex: 2503.94 que na verdade deveria ser 250.39)
            if valor > 1000:
                valor_corrigido = valor / 10
                if valor_corrigido < 1000:
                    valor = valor_corrigido

            # Formatação estilo brasileiro
            valor_formatado = f"{valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

            # Remover ",00" se o valor for inteiro
            if valor_formatado.endswith(",00"):
                valor_formatado = valor_formatado.replace(",00", "")

            return valor_formatado
        except:
            return valor  # retorna como está se não for possível formatar

    for col in colunas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].apply(ajustar_valor)
    return df




# Seleção do produto

col1, col2 = st.columns(2)
with col1:
    produto_selecionado = st.selectbox("Selecione um produto", df_produtos["Nome do Produto"].unique())
    produto_info = df_produtos[df_produtos["Nome do Produto"] == produto_selecionado].iloc[0]

with col2:
    quantidade = st.number_input("Quantidade", min_value=1, step=1)


# Exibir detalhes
st.subheader("📦 Informações do Produto")


# Exibir informações do produto selecionado
st.write(f"**Categoria** {produto_info['Categoria']}")
st.write(f"**Descrição:** {produto_info['Descrição']}")
st.write(f"**Preço Base (R$):** {produto_info['Preço Base (R$)']}") 
st.write(f"**Impostos (R$):** {produto_info['Imposto de Importação (%)']}")
st.write(f"**ICMS (%):** {produto_info['ICMS (%)']}")
st.write(f"**IPI (%):** {produto_info['IPI (%)']}")

## Esse é o cálculo do preço final
st.markdown(f"### :orange[**Preço Final (R$):** {produto_info['Preço Final c/ Impostos (R$)']:.2f}] ")


# Adicionar ao carrinho
if st.button("➕ Adicionar ao Carrinho"):
    try:
        item = {
            "Produto": produto_selecionado,
            "Categoria": produto_info["Categoria"],
            "Quantidade": quantidade,
            "Valor Unitário (R$)": produto_info["Preço Final c/ Impostos (R$)"],
            "Valor Total (R$)": quantidade * produto_info["Preço Final c/ Impostos (R$)"]
        }
        st.session_state.carrinho.append(item)
        st.success("Produto adicionado ao carrinho.")
    except Exception as e:
        st.error(f"Erro ao adicionar item ao carrinho: {e}")

# Função para formatar o valor preço final
def formatar_preco(total_geral):
    return f"{total_geral:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def formatar_df_carrinho(df_carrinho):
    def formatar_preco(valor):
        return f"{valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

    # Garantir que as colunas de valor sejam numéricas
    df_carrinho["Valor Unitário (R$)"] = pd.to_numeric(df_carrinho["Valor Unitário (R$)"], errors="coerce")
    df_carrinho["Valor Total (R$)"] = pd.to_numeric(df_carrinho["Valor Total (R$)"], errors="coerce")

    # Calcular o total geral antes de formatar
    total_geral = df_carrinho["Valor Total (R$)"].sum()

    # Formatar colunas
    df_carrinho["Valor Unitário (R$)"] = df_carrinho["Valor Unitário (R$)"].apply(formatar_preco)
    df_carrinho["Valor Total (R$)"] = df_carrinho["Valor Total (R$)"].apply(formatar_preco)

    # Linha de total geral
    linha_total = {
        "Produto": "🧾 TOTAL GERAL",
        "Categoria": "",
        "Quantidade": "",
        "Valor Unitário (R$)": "",
        "Valor Total (R$)": formatar_preco(total_geral)
    }

    return pd.concat([df_carrinho, pd.DataFrame([linha_total])], ignore_index=True)

# Mostrar carrinho com opção de remover
if st.session_state.carrinho:
    st.subheader("🛒 Carrinho de Compras")
    df_carrinho = pd.DataFrame(st.session_state.carrinho)

    # Adicionar coluna de remoção
    df_carrinho["Remover"] = False

    # Editor interativo com checkbox para exclusão
    editado = st.data_editor(
        df_carrinho,
        column_config={
            "Remover": st.column_config.CheckboxColumn("❌ Excluir Produto")
        },
        disabled=["Produto", "Categoria", "Quantidade", "Valor Unitário (R$)", "Valor Total (R$)"],
        hide_index=True,
        use_container_width=True,
        key="editor_remocao"
    )

    # Verifica itens removidos
    removidos = editado[editado["Remover"] == True]["Produto"].tolist()
    if removidos:
        st.warning(f"🗑️ Os seguintes produtos foram removidos do carrinho: {', '.join(removidos)}")

    # Atualiza o carrinho
    df_filtrado = editado[editado["Remover"] == False].drop(columns=["Remover"])
    st.session_state.carrinho = df_filtrado.to_dict(orient="records")

    # Recalcular total
    if not df_filtrado.empty:
        total_geral = df_filtrado["Valor Total (R$)"].sum()
        st.markdown(f"# :green[**💰 Total da Compra: R$ {formatar_preco(total_geral)}**]")

        # Formulário do comprador
        st.subheader("👤 Finalizar Compra")
        nome = st.text_input("Nome do Comprador")
        empresa = st.text_input("Empresa / Equipe")
        email = st.text_input("Email")
        encargo_percentual = 0.20
        
        if st.button("💾 Finalizar Pedido"):
            if not nome or not empresa or not email:
                st.warning("⚠️ Preencha todos os campos antes de finalizar.")
            else:
                try:
                    registros = []
                    for item in st.session_state.carrinho:
                        # Conversão segura para float
                        valor_unit = item["Valor Unitário (R$)"]
                        if isinstance(valor_unit, str):
                            valor_unit = float(str(valor_unit).replace(".", "").replace(",", "."))

                        valor_total = item["Valor Total (R$)"]
                        if isinstance(valor_total, str):
                            valor_total = float(str(valor_total).replace(".", "").replace(",", "."))

                        encargo = round(valor_total * encargo_percentual, 2)

                        nova_venda = {
                            "Data da Compra": datetime.today().strftime('%Y-%m-%d'),
                            "Nome do Comprador": nome,
                            "Empresa": empresa,
                            "Email": email,
                            "Produto": item["Produto"],
                            "Categoria": item["Categoria"],
                            "Quantidade": item["Quantidade"],
                            "Valor Unitário (R$)": valor_unit,
                            "Valor Total (R$)": valor_total,
                            "Encargo (%)": encargo_percentual * 100,
                            "Encargo (R$)": encargo
                        }
                        registros.append(nova_venda)

                    df_vendas = pd.DataFrame(registros)
                    nome_arquivo = f"venda_{nome.replace(' ', '_').upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                    caminho_arquivo = os.path.join(vendas_dir, nome_arquivo)
                    df_vendas.to_csv(caminho_arquivo, index=False)

                    st.success("✅ Pedido finalizado com sucesso!")

                    with open(caminho_arquivo, "rb") as file:
                        st.download_button(
                            label="⬇️ Baixar Pedido em CSV",
                            data=file,
                            file_name=nome_arquivo,
                            mime="text/csv"
                        )

                    st.session_state.carrinho = []

                except Exception as e:
                    st.error(f"Erro ao registrar vendas: {e}")



    else:
        st.info("Seu carrinho está vazio.")
else:
    st.info("Seu carrinho está vazio.")


st.header("Envie o csv nesse email abaixo: ")
st.link_button("anderson.seixas@ifro.edu.br", "anderson.seixas@ifro.edu.br")