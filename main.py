import streamlit as st
import pandas as pd
from blockchain import PythonBlockchain
import fio_coin
import tech_token
import gold_py

# ==========================================
# Configuração da Página
# ==========================================
st.set_page_config(
    page_title="PyChain Dashboard",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada para dar um ar "Tech"
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; border-radius: 10px; padding: 15px;}
    .stButton>button {width: 100%; border-radius: 5px; height: 3em;}
    .reportview-container {background: #ffffff;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# Inicialização do Estado (Singleton Pattern no Streamlit)
# ==========================================
if 'blockchain' not in st.session_state:
    # 1. Instancia a Blockchain apenas uma vez
    chain = PythonBlockchain(difficulty=2)
    
    # 2. Faz o deploy dos contratos
    chain.deploy_contract(fio_coin.moeda)
    chain.deploy_contract(tech_token.moeda)
    chain.deploy_contract(gold_py.moeda)
    
    # 3. Distribuição Inicial (Genesis)
    # Dá dinheiro para testes iniciais
    chain.add_transaction("system_genesis", fio_coin.moeda.address, "transfer", recipient="Ricardo", amount=1000)
    chain.add_transaction("system_genesis", tech_token.moeda.address, "transfer", recipient="DevTeam", amount=5000)
    chain.add_transaction("system_genesis", gold_py.moeda.address, "transfer", recipient="Alice", amount=50)
    
    # Minera o primeiro bloco para validar essas transações iniciais
    chain.mine()

    st.session_state['blockchain'] = chain
    st.session_state['logs'] = ["Sistema iniciado. Genesis Block minerado."]

# Alias para facilitar o acesso
chain = st.session_state.blockchain

# ==========================================
# BARRA LATERAL (WALLET & TRANSAÇÕES)
# ==========================================
with st.sidebar:
    st.header("💳 Carteira (Simulator)")
    
    # Seleção de Persona
    sender = st.selectbox("Quem é você?", ["Ricardo", "Alice", "Bob", "DevTeam"])
    
    st.markdown("---")
    st.subheader("Nova Transação")
    
    recipient = st.text_input("Para quem enviar?", value="Alice")
    
    # Seleção de Moeda Dinâmica
    token_options = {
        "FioCoin ($FIO)": fio_coin.moeda,
        "TechToken ($TCH)": tech_token.moeda,
        "GoldPy ($GLD)": gold_py.moeda
    }
    selected_token_name = st.selectbox("Qual moeda?", list(token_options.keys()))
    selected_contract = token_options[selected_token_name]
    
    amount = st.number_input("Quantidade", min_value=1, value=10)
    
    if st.button("🚀 Enviar Transação"):
        # Adiciona à Mempool
        chain.add_transaction(
            sender=sender,
            contract_address=selected_contract.address,
            function="transfer",
            recipient=recipient,
            amount=int(amount)
        )
        st.toast(f"Transação enviada para Mempool! Aguardando mineração.", icon="⏳")

    st.markdown("---")
    st.info(f"Endereço do Contrato {selected_token_name.split(' ')[1]}: \n`{selected_contract.address}`")

# ==========================================
# PAINEL PRINCIPAL
# ==========================================
st.title("🔗 PyChain: Blockchain Engineering Demo")
st.markdown("#### Simulação de arquitetura Account-Based com Smart Contracts Python")

# 1. Métricas do Topo
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Altura da Chain", f"{len(chain.chain)} Blocos")
with col2:
    st.metric("Transações Pendentes", f"{len(chain.pending_transactions)}")
with col3:
    st.metric("Dificuldade", f"{chain.difficulty} zeros")
with col4:
    if st.button("⛏️ MINERAR BLOCO", type="primary"):
        if len(chain.pending_transactions) == 0:
            st.warning("Não há transações para minerar.")
        else:
            with st.spinner('Minerando Proof of Work...'):
                block, logs = chain.mine()
                st.session_state['logs'].extend(logs)
                st.success(f"Bloco #{block.index} minerado! Hash: {block.hash[:15]}...")
                st.balloons()

# ==========================================
# ABAS DE VISUALIZAÇÃO
# ==========================================
tab1, tab2, tab3 = st.tabs(["🔍 Explorer", "💰 Saldos (State)", "📜 Logs do Sistema"])

with tab1:
    st.subheader("Blockchain Explorer")
    
    # Visualizar Blocos como JSON Expansível
    for block in reversed(chain.chain):
        with st.expander(f"Bloco #{block.index} - Hash: {block.hash[:20]}..."):
            st.json(block.__dict__)

with tab2:
    st.subheader("Estado Global dos Contratos")
    
    # Criar um DataFrame bonito para mostrar os saldos
    # Coletamos os dados brutos do estado dos contratos
    data = []
    
    # Para cada contrato registrado
    for addr, contract in chain.contracts.items():
        symbol = contract.state['symbol']
        # Para cada usuário que tem saldo naquele contrato
        for user, balance in contract.state['balances'].items():
            if balance > 0: # Só mostra quem tem saldo
                data.append({"Token": symbol, "Usuário": user, "Saldo": balance, "Endereço Contrato": addr})
    
    if data:
        df = pd.DataFrame(data)
        # Pivot table para ficar igual excel: Linhas=Usuários, Colunas=Tokens
        df_pivot = df.pivot_table(index="Usuário", columns="Token", values="Saldo", fill_value=0)
        st.dataframe(df_pivot, use_container_width=True)
    else:
        st.info("Nenhum saldo registrado ainda.")

with tab3:
    st.subheader("Logs da EVM (Virtual Machine)")
    for log in reversed(st.session_state['logs']):
        st.code(log, language="text")

# Rodapé
st.markdown("---")
st.caption("Desenvolvido para Portfólio de Engenharia de Computação - 2025")