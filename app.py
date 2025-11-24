import os
import streamlit as st
import pandas as pd
import random
import torch
import gc


# Otimizações de sistema
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE" 

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from mangaba import Agent 

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="YBY.AI - Sistema Agroecológico",
    page_icon="🌵",
    layout="wide"
)

# --- 1. CARREGAMENTO DO MODELO (ENGINE) ---
@st.cache_resource(show_spinner=False)
def load_engine():
    BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    ADAPTER_REPO = "YsraelJS/tinyllama-solo-management-adapters"
    
    container = st.empty()
    container.info("⚙️ Carregando Cérebro Digital YBY (Isso pode demorar na 1ª vez)...")
    
    try:
        gc.collect()
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        
        # Carregamento otimizado para CPU/Windows
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            device_map="cpu", 
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        
        model = PeftModel.from_pretrained(base_model, ADAPTER_REPO)
        model = model.merge_and_unload() 
        
        container.empty()
        return tokenizer, model

    except Exception as e:
        container.error(f"⚠️ Modo Offline Ativado (Erro local: {e})")
        return None, None

tokenizer, model = load_engine()
MODE = "IA Local (TinyLlama)" if model else "Modo Nuvem/Simulação"

# --- 2. FUNÇÃO DE INFERÊNCIA ---
def run_agent(agent: Agent, prompt_text: str, max_tokens=250):
    """
    Gera resposta usando IA Local ou Fallback Simulado.
    """
    if model and tokenizer:
        try:
            system = f"Você é {agent.role}. {agent.backstory}. Objetivo: {agent.goal}"
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt_text}
            ]
            
            input_ids = tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, return_tensors="pt"
            )
            
            with torch.no_grad():
                outputs = model.generate(
                    input_ids, 
                    max_new_tokens=max_tokens, 
                    do_sample=True, 
                    temperature=0.4, 
                    top_p=0.9
                )
            
            return tokenizer.decode(outputs[0][input_ids.shape[1]:], skip_special_tokens=True)
        except Exception as e:
            return f"Erro inferência local: {e}"
    else:
        # FALLBACK INTELIGENTE (SIMULAÇÃO)
        # Se o modelo não carregar, geramos respostas baseadas na lógica para não travar a demo
        if "ecológico" in prompt_text.lower():
            return (
                "**Plano de Ação Regenerativa (Simulado):**\n\n"
                "1. **Cobertura Morta (Mulching):** Essencial para reter a pouca umidade do semiárido e proteger o solo do sol direto.\n"
                "2. **Adubação Orgânica:** Incorpore esterco curtido ou compostagem para aumentar a capacidade de retenção de água (CRA).\n"
                "3. **Sistema de Gotejamento:** Recomendado para economizar água dado o nível de umidade atual.\n"
                "4. **Plantio em Nível:** Para evitar erosão em chuvas torrenciais."
            )
        else:
            return "Recomendação: **NPK 14-35-14** (Correção de Fósforo necessária)."

# --- 3. SIMULADOR IOT ---
st.sidebar.image("https://img.shields.io/badge/YBY.AI-Semiárido_Tech-orange", use_container_width=True)
st.sidebar.markdown(f"**Motor:** `{MODE}`")

if 'iot_data' not in st.session_state:
    # Dados padrão simulando um dia quente no nordeste
    st.session_state['iot_data'] = {
        'Temperatura': 32.5, 
        'Umidade': 45.0, 
        'Solo_Umid': 28.0, # Solo seco
        'Tipo_Solo': 'Arenoso',
        'Cultura': 'Milho',
        'N': 15, 'P': 8, 'K': 12
    }

if st.sidebar.button("🔄 Ler Sensores (Tempo Real)"):
    solos = ['Arenoso', 'Argiloso', 'Cascalho', 'Terra Roxa']
    culturas = ['Milho', 'Palma Forrageira', 'Feijão Corda', 'Mandioca', 'Algodão']
    
    st.session_state['iot_data'] = {
        'Temperatura': round(random.uniform(28.0, 39.0), 1), # Calor
        'Umidade': round(random.uniform(30.0, 60.0), 1),
        'Solo_Umid': round(random.uniform(10.0, 45.0), 1), # Tende a seco
        'Tipo_Solo': random.choice(solos),
        'Cultura': random.choice(culturas),
        'N': random.randint(5, 50),
        'P': random.randint(5, 40),
        'K': random.randint(5, 40)
    }
    st.sidebar.toast("Dados atualizados via Satélite/IoT!", icon="🛰️")

d = st.session_state['iot_data']

# Exibição Sidebar
c1, c2 = st.sidebar.columns(2)
c1.metric("🌡️ Temp", f"{d['Temperatura']}°C")
c2.metric("💧 Ar", f"{d['Umidade']}%")
c1.metric("🌱 Solo", f"{d['Solo_Umid']}%", delta="-Baixa" if d['Solo_Umid'] < 30 else "Normal")

st.sidebar.divider()
st.sidebar.info(f"Bioma/Solo: **{d['Tipo_Solo']}**")
st.sidebar.warning(f"Cultura: **{d['Cultura']}**")
st.sidebar.markdown("### Nutrientes (NPK)")
cn, cp, ck = st.sidebar.columns(3)
cn.metric("N", d['N'])
cp.metric("P", d['P'])
ck.metric("K", d['K'])

# --- 4. INTERFACE PRINCIPAL ---
st.title("🌵 YBY.AI: Inteligência Regenerativa")
st.markdown("Plataforma de manejo para solos desafiadores e agricultura de precisão.")

tab1, tab2 = st.tabs(["📊 Diagnóstico & Plano de Ação", "💬 Consultor YBY"])

# --- ABA 1: RELATÓRIO COMPLETO ---
with tab1:
    st.subheader("Diagnóstico Integrado")
    
    col_left, col_right = st.columns([1, 1.5])
    
    with col_left:
        st.markdown("#### 1. Correção Química (Imediata)")
        st.caption("Baseado no modelo Fine-Tuned (TinyLlama)")
        
        if st.button("💊 Gerar Recomendação de NPK"):
            with st.spinner("Calculando estequiometria..."):
                agente_quimico = Agent(
                    role="Técnico Agrícola",
                    goal="Recomendar fertilizante NPK exato.",
                    backstory="Especialista em tabelas nutricionais.",
                )
                prompt_quimico = (
                    f"Com temperatura {d['Temperatura']}, umidade {d['Umidade']}, "
                    f"solo {d['Tipo_Solo']} para {d['Cultura']}, N={d['N']}, P={d['P']}, K={d['K']}. "
                    f"Qual fertilizante usar?"
                )
                res_quimica = run_agent(agente_quimico, prompt_quimico)
                st.success("Fertilizante Recomendado:")
                st.markdown(f"### {res_quimica}")

    with col_right:
        st.markdown("#### 2. Plano de Manejo Ecológico (Médio Prazo)")
        st.caption("Análise regenerativa para solos do semiárido/tropicais.")
        
        if st.button("🌳 Gerar Plano de Ação Ecológica"):
            with st.spinner("Consultando base de agroecologia..."):
                
                # AGENTE ECOLÓGICO (A Novidade)
                agente_eco = Agent(
                    role="Especialista em Agroecologia e Semiárido",
                    goal="Criar plano de ação para retenção de água e vida no solo.",
                    backstory="Você é especialista em convivência com o semiárido. Foco em matéria orgânica e água.",
                )
                
                # Prompt enriquecido para forçar lógica ecológica
                prompt_eco = (
                    f"Crie um plano de ação curto (3 itens) para tratar um solo do tipo {d['Tipo_Solo']} "
                    f"com umidade crítica de {d['Solo_Umid']}% e temperatura de {d['Temperatura']}°C. "
                    f"O foco é a cultura de {d['Cultura']}. "
                    f"Sugira técnicas de retenção de água, cobertura de solo e adubação orgânica."
                )
                
                res_eco = run_agent(agente_eco, prompt_eco, max_tokens=400)
                
                st.info("Plano de Regeneração Sugerido:")
                st.markdown(res_eco)

# --- ABA 2: CHATBOT ---
with tab2:
    st.subheader("Consultor de Campo")
    st.caption("Tire dúvidas sobre pragas, sistemas agroflorestais (SAFs) ou manejo.")
    
    chat_agent = Agent(
        role="Assistente YBY", 
        goal="Ajudar o produtor", 
        backstory="Assistente amigável focado em agricultura sustentável."
    )

    if "history" not in st.session_state:
        st.session_state.history = []

    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ex: Como combater a cochonilha na palma?"):
        st.session_state.history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Analisando..."):
                resp = run_agent(chat_agent, prompt)
                st.write(resp)
                st.session_state.history.append({"role": "assistant", "content": resp})
