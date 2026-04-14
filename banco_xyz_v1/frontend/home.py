import streamlit as st
from app.data_loader import get_client_list
from app.graph import run_langgraph
from utils import navbar, header, section_divider


# --------------------------------------------------------------
# CONFIGURAÇÃO INICIAL DA PÁGINA
# --------------------------------------------------------------
# Define:
# - Título exibido na aba do navegador
# - Layout em tela cheia (wide)
# - Ícone da aba (emoji 🏦)


st.set_page_config(page_title="Banco XYZ", layout="wide", page_icon="🏦")

# Renderiza o cabeçalho visual (faixa superior azul + título)
header() 
# Renderiza o menu superior de navegação (Home, Clientes, Relatórios, etc.)
navbar()
# Linha divisora estilizada entre o cabeçalho e o conteúdo da página
section_divider()


# --------------------------------------------------------------
# TÍTULO PRINCIPAL
# --------------------------------------------------------------
# Aqui você poderia usar page_title(), mas optou por HTML,
# então exibimos um título estilizado manualmente.

st.markdown("""
<div style="
    font-size: 26px;
    font-weight: 700;
    color: #0A2E57;
    margin-top: 10px;
    margin-bottom: 10px;">
📊 Gerar Relatório
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------------------
# INICIALIZAÇÃO DO SESSION_STATE
# --------------------------------------------------------------
# Esse “estado global” guarda os dados disponíveis entre páginas.
# Aqui garantimos que as chaves existem, mesmo que vazias.

if "resultado" not in st.session_state:
    st.session_state.resultado = None
if "cliente_id" not in st.session_state:
    st.session_state.cliente_id = None
 
# --------------------------------------------------------------
# CARREGA A LISTA DE CLIENTES DO EXCEL
# --------------------------------------------------------------
# get_client_list() retorna um dicionário simplificado: {id, nome}   

clientes = get_client_list()

# Cria um dicionário no formato:
# “Nome (CLI001)” → "CLI001"
# para exibir na seleção do Streamlit
opcoes = {f"{c['nome']} ({c['id']})": c['id'] for c in clientes}

# Componente visual para o usuário escolher o cliente
selecionado = st.selectbox("Selecione um cliente:", list(opcoes.keys()))

# --------------------------------------------------------------
# BOTÃO DE GERAÇÃO DO RELATÓRIO
# --------------------------------------------------------------
# Quando clicado:
# 1. Guarda o ID do cliente no session_state
# 2. Executa o LangGraph com esse ID
# 3. Salva o resultado (dados + relatório da IA)
# 4. Mostra um success

if st.button("Gerar Relatório"):
    with st.spinner("Gerando relatório..."):
         # Salva o ID do cliente escolhido
        st.session_state.cliente_id = opcoes[selecionado]
        # Executa o fluxo do LangGraph (data_loader -> prompt -> LLM)
        st.session_state.resultado = run_langgraph(st.session_state.cliente_id)
        # Mensagem visual confirmando sucesso
    st.success("Relatório gerado! Navegue pelo menu acima.")