import streamlit as st
import os
import random
from mangaba import Agent, Task, Crew, Process

# --- 0. CONFIGURAÇÃO DE AMBIENTE ---
# Define o modelo Gemini Flash (Mais rápido e barato para Hackathon)
os.environ["MODEL_NAME"] = "gemini-1.5-flash"
os.environ["LLM_PROVIDER"] = "google"

# Gerenciamento de Chaves (Nuvem vs Local)
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
else:
    # Se não houver secrets, verifica variável de ambiente local
    if "GOOGLE_API_KEY" not in os.environ:
        st.warning("⚠️ API Key não encontrada! Configure os 'Secrets' no Streamlit Cloud.")

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="YBY.AI - Inteligência Agronômica",
    page_icon="🌱",
    layout="wide"
)

# --- 1. MOTOR DE INTELIGÊNCIA (MANGABA v2.0) ---
def executar_crew(role, goal, backstory, input_usuario):
    """
    Função wrapper que cria e executa uma Crew do Mangaba para uma tarefa específica.
    """
    try:
        # 1. Definir o Agente
        agente = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False
        )

        # 2. Definir a Tarefa
        tarefa = Task(
            description=input_usuario,
            expected_output="Uma resposta técnica, formatada em Markdown, direta e em português do Brasil.",
            agent=agente
        )

        # 3. Orquestrar a Crew
        equipe = Crew(
            agents=[agente],
            tasks=[tarefa],
            process=Process.SEQUENTIAL,
            verbose=True
        )

        # 4. Executar
        resultado = equipe.kickoff()
        return resultado

    except Exception as e:
        return f"❌ Erro na execução da IA: {str(e)}. Verifique sua Chave de API."

# --- 2. SIMULADOR IOT (BARRA LATERAL) ---
st.sidebar.image("https://img.shields.io/badge/YBY.AI-Powered_by_Gemini-green", use_container_width=True)
st.sidebar.markdown("### 📡 Telemetria em Tempo Real")

# Inicialização do Estado
if 'iot_data' not in st.session_state:
    st.session_state['iot_data'] = {
        'Temperatura': 29.5, 'Umidade': 40.0, 'Solo_Umid': 25.0,
        'Tipo_Solo': 'Arenoso', 'Cultura': 'Milho',
        'N': 12, 'P': 8, 'K': 15
    }

# Botão de Atualização dos Sensores
if st.sidebar.button("🔄 Ler Sensores (Simulação)"):
    culturas = ['Milho', 'Feijão', 'Palma Forrageira', 'Mandioca', 'Caju']
    solos = ['Arenoso', 'Argiloso', 'Misto', 'Salino']
    
    st.session_state['iot_data'] = {
        'Temperatura': round(random.uniform(26, 39), 1),
        'Umidade': round(random.uniform(30, 65), 1),
        'Solo_Umid': round(random.uniform(10, 55), 1), # Tende a seco (Semiárido)
        'Tipo_Solo': random.choice(solos),
        'Cultura': random.choice(culturas),
        'N': random.randint(5, 50),
        'P': random.randint(5, 40),
        'K': random.randint(5, 50)
    }
    st.sidebar.success("Dados atualizados!")

d = st.session_state['iot_data']

# Exibição dos Cards
col1, col2 = st.sidebar.columns(2)
col1.metric("🌡️ Temp", f"{d['Temperatura']}°C")
col2.metric("💧 Solo", f"{d['Solo_Umid']}%", delta="-Crítico" if d['Solo_Umid'] < 30 else "Estável")
st.sidebar.info(f"Solo: **{d['Tipo_Solo']}** | Cultura: **{d['Cultura']}**")

st.sidebar.markdown("### Nutrientes (Análise Rápida)")
col_n, col_p, col_k = st.sidebar.columns(3)
col_n.metric("N", d['N'])
col_p.metric("P", d['P'])
col_k.metric("K", d['K'])

# --- 3. INTERFACE PRINCIPAL ---
st.title("🥭 YBY.AI: Inteligência do Semiárido")
st.markdown("Plataforma de decisão agronômica focada em precisão e sustentabilidade.")

tab1, tab2 = st.tabs(["📊 Painel de Decisão", "💬 Consultor Virtual"])

# ABA 1: RELATÓRIOS ESTRUTURADOS
with tab1:
    st.subheader("Diagnóstico e Prescrição")
    
    col_left, col_right = st.columns(2)
    
    # --- COLUNA 1: QUÍMICA DE PRECISÃO ---
    with col_left:
        st.markdown("#### 1. Correção Química (Dose Econômica)")
        st.caption("Cálculo estequiométrico para evitar desperdício de insumos.")
        
        if st.button("💊 Calcular Dosagem (Kg/ha)", use_container_width=True):
            with st.spinner("Realizando balanço nutricional..."):
                
                # Prompt Engenharia: Focado em economia e precisão
                prompt_quimico = (
                    f"ATUE COMO UM AGRÔNOMO DE PRECISÃO.\n"
                    f"DADOS REAIS DOS SENSORES:\n"
                    f"- Cultura: {d['Cultura']}\n"
                    f"- Solo: {d['Tipo_Solo']}\n"
                    f"- Níveis Atuais: Nitrogênio={d['N']} mg, Fósforo={d['P']} mg, Potássio={d['K']} mg.\n\n"
                    f"Sua missão é economizar dinheiro do produtor e salvar o solo.\n"
                    f"1. Identifique qual nutriente é o limitante (Lei de Liebig).\n"
                    f"2. Recomende APENAS o fertilizante necessário (ex: Ureia, Superfosfato, Cloreto).\n"
                    f"3. CALCULE A DOSE EXATA em kg/hectare para uma produtividade média.\n"
                    f"4. ALERTA: Se os níveis estiverem bons, diga explicitamente: 'Não aplicar nada'. Evite excessos."
                )
                
                res = executar_crew(
                    role="Engenheiro de Fertilidade do Solo",
                    goal="Gerar recomendação de adubação precisa, econômica e sem desperdícios.",
                    backstory="Você é um especialista rigoroso. Você odeia desperdício de fertilizante. Você segue estritamente tabelas técnicas.",
                    input_usuario=prompt_quimico
                )
                
                st.success("Prescrição Gerada:")
                st.markdown(res)

    # --- COLUNA 2: MANEJO ECOLÓGICO ---
    with col_right:
        st.markdown("#### 2. Manejo Regenerativo")
        st.caption("Estratégias de convivência com a seca e saúde do solo.")
        
        if st.button("🌳 Plano de Ação Ecológico", use_container_width=True):
            with st.spinner("Analisando indicadores ambientais..."):
                
                # Prompt Engenharia: Focado em semiárido e água
                prompt_eco = (
                    f"Crie um protocolo de manejo para o Semiárido Brasileiro.\n"
                    f"Condições: Cultura {d['Cultura']}, Solo {d['Tipo_Solo']}.\n"
                    f"Clima Atual: Umidade do Solo em {d['Solo_Umid']}% (Crítico < 30) e Temp {d['Temperatura']}°C.\n"
                    f"Gere 3 ações práticas focadas em:\n"
                    f"1. Retenção de Água (ex: Mulching, Hidrogel).\n"
                    f"2. Matéria Orgânica (ex: Esterco, Compostagem).\n"
                    f"3. Consórcio ou Rotação ideal para este solo."
                )
                
                res = executar_crew(
                    role="Engenheiro Agroecológico",
                    goal="Restaurar a vida do solo e maximizar o uso da água.",
                    backstory="Especialista em Agricultura Sintrópica e convivência com o Semiárido. Foco em soluções naturais.",
                    input_usuario=prompt_eco
                )
                
                st.info("Plano Sustentável:")
                st.markdown(res)

# ABA 2: CHATBOT
with tab2:
    st.subheader("Assistente de Campo YBY")
    st.caption("Tire dúvidas sobre pragas, doenças e operações.")

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
                res = executar_crew(
                    role="Assistente Técnico Virtual",
                    goal="Responder dúvidas do produtor de forma simples e direta.",
                    backstory=(
                        "Você é um assistente amigável para produtores rurais. "
                        "Responda apenas sobre agricultura. "
                        "Se perguntarem sobre outros assuntos, recuse educadamente."
                    ),
                    input_usuario=user_input
                )
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
