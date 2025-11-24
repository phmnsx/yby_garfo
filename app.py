import streamlit as st
import os
import random
import time
from mangaba import Agent

# --- 0. CONFIGURAÇÃO DE AMBIENTE E SEGURANÇA ---
# Configura para usar o modelo Flash (mais rápido para demos)
os.environ["MODEL_NAME"] = "gemini-1.5-flash"
os.environ["LLM_PROVIDER"] = "google"

# Tenta carregar a chave dos Segredos do Streamlit (Nuvem)
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
else:
    # Fallback para local (se você tiver um .env ou quiser testar sem secrets)
    if "GOOGLE_API_KEY" not in os.environ:
        # Dica visual se a chave faltar
        st.warning("⚠️ API Key não detectada! Configure os 'Secrets' no Streamlit Cloud.")

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="YBY.AI - Monitoramento Inteligente",
    page_icon="🌱",
    layout="wide"
)

# --- 1. DEFINIÇÃO DOS AGENTES (GUARDRAILS) ---
# O "Backstory" atua como um guardrail (trava de segurança)
GUARDRAIL_PROMPT = """
VOCÊ É UM SISTEMA CRÍTICO DE AGRICULTURA.
REGRAS ABSOLUTAS:
1. Responda APENAS sobre agricultura, manejo de solo, pragas e clima.
2. Se perguntarem sobre política, esportes ou receitas culinárias: RECUSE. Diga: "Sou calibrado apenas para assistência técnica rural."
3. Seja técnico, direto e use linguagem de extensionista rural.
"""

@st.cache_resource
def get_agents():
    """Cria os agentes Mangaba uma única vez para economizar recursos."""
    return {
        "quimico": Agent(
            role="Engenheiro Agrônomo (Nutrição)",
            goal="Calcular correção de solo NPK.",
            backstory=f"{GUARDRAIL_PROMPT} Especialista em química do solo e fertilizantes comerciais.",
            verbose=True
        ),
        "ecologico": Agent(
            role="Especialista em Agroecologia",
            goal="Sugerir manejo sustentável para seca.",
            backstory=f"{GUARDRAIL_PROMPT} Especialista em semiárido, retenção de água e adubação verde.",
            verbose=True
        ),
        "chat": Agent(
            role="Assistente de Campo",
            goal="Tirar dúvidas rápidas do produtor.",
            backstory=f"{GUARDRAIL_PROMPT} Assistente virtual amigável para WhatsApp rural.",
            verbose=True
        )
    }

# --- 2. SIMULADOR IOT (DADOS) ---
st.sidebar.image("https://img.shields.io/badge/YBY.AI-Powered_by_Gemini_Flash-blue", use_container_width=True)

if 'iot_data' not in st.session_state:
    st.session_state['iot_data'] = {
        'Temperatura': 29.5, 'Umidade': 40.0, 'Solo_Umid': 25.0,
        'Tipo_Solo': 'Arenoso', 'Cultura': 'Milho',
        'N': 12, 'P': 8, 'K': 15
    }

if st.sidebar.button("🔄 Atualizar Sensores (IoT)"):
    culturas = ['Milho', 'Feijão', 'Palma Forrageira', 'Mandioca', 'Caju']
    solos = ['Arenoso', 'Argiloso', 'Misto', 'Salino']
    
    st.session_state['iot_data'] = {
        'Temperatura': round(random.uniform(26, 39), 1),
        'Umidade': round(random.uniform(30, 65), 1),
        'Solo_Umid': round(random.uniform(10, 55), 1), # Tende a seco no semiárido
        'Tipo_Solo': random.choice(solos),
        'Cultura': random.choice(culturas),
        'N': random.randint(5, 50),
        'P': random.randint(5, 40),
        'K': random.randint(5, 50)
    }
    st.sidebar.success("📡 Dados recebidos da estação!")

d = st.session_state['iot_data']

# Métricas Visuais
c1, c2 = st.sidebar.columns(2)
c1.metric("🌡️ Temp", f"{d['Temperatura']}°C")
c2.metric("💧 Solo", f"{d['Solo_Umid']}%", delta="-Crítico" if d['Solo_Umid'] < 30 else "Estável")
st.sidebar.info(f"Solo: **{d['Tipo_Solo']}** | Cultura: **{d['Cultura']}**")

st.sidebar.markdown("### Nutrientes (mg/dm³)")
col_n, col_p, col_k = st.sidebar.columns(3)
col_n.metric("N", d['N'])
col_p.metric("P", d['P'])
col_k.metric("K", d['K'])

# --- 3. INTERFACE PRINCIPAL ---
st.title("🥭 YBY.AI: Inteligência do Semiárido")
st.markdown("Sistema de decisão agronômica em tempo real.")

tab1, tab2 = st.tabs(["📊 Diagnóstico & Manejo", "💬 Consultor Virtual"])

# ABA 1: RELATÓRIOS TÉCNICOS
with tab1:
    st.subheader("Central de Decisão")
    
    col_left, col_right = st.columns(2)
    
    # --- BOTÃO 1: QUÍMICO ---
    with col_left:
        st.markdown("#### 1. Correção Química (NPK)")
        st.caption("Foco em produtividade imediata.")
        
        if st.button("💊 Gerar Recomendação Química", use_container_width=True):
            with st.spinner("Agente Químico calculando dosagem..."):
                prompt = (
                    f"Analise estes dados de solo do semiárido: Solo {d['Tipo_Solo']}, Cultura {d['Cultura']}. "
                    f"Níveis: N={d['N']}, P={d['P']}, K={d['K']}. Temp={d['Temperatura']}C. "
                    f"Recomende um fertilizante comercial (ex: Ureia, NPK 14-35-14) e explique o motivo técnico em 2 linhas."
                )
                try:
                    agentes = get_agents()
                    res = agentes["quimico"].chat(prompt)
                    st.success("Recomendação Aprovada:")
                    st.markdown(res)
                except Exception as e:
                    st.error(f"Erro na API: {e}")

    # --- BOTÃO 2: ECOLÓGICO ---
    with col_right:
        st.markdown("#### 2. Manejo Ecológico")
        st.caption("Foco em sustentabilidade e água.")
        
        if st.button("🌳 Gerar Plano Regenerativo", use_container_width=True):
            with st.spinner("Agente Ecológico consultando base..."):
                prompt = (
                    f"Crie um plano de ação para {d['Cultura']} no semiárido brasileiro. "
                    f"Situação: Solo {d['Tipo_Solo']}, Umidade {d['Solo_Umid']}% (Baixa), Temp {d['Temperatura']}C. "
                    f"Liste 3 técnicas de convivência com a seca (ex: Mulching, Hidrogel, Palma) para salvar a lavoura."
                )
                try:
                    agentes = get_agents()
                    res = agentes["ecologico"].chat(prompt)
                    st.info("Plano de Ação Sustentável:")
                    st.markdown(res)
                except Exception as e:
                    st.error(f"Erro na API: {e}")

# ABA 2: CHATBOT
with tab2:
    st.subheader("Assistente de Campo")
    st.caption("Tire dúvidas operacionais. Ex: 'Como combater a lagarta do cartucho?'")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Digite sua dúvida..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Consultando base técnica..."):
                try:
                    agentes = get_agents()
                    # O agente 'chat' já tem o guardrail no prompt
                    response = agentes["chat"].chat(user_input)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")
