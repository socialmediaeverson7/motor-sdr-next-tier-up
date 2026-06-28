import os
import time
import requests
from datetime import datetime
import streamlit as st

# 1. A REGRA DE OURO DO STREAMLIT: A interface carrega primeiro!
st.set_page_config(page_title="Motor SDR - Next Tier Up", page_icon="🎯", layout="wide")

# 2. Desligar telemetria ANTES de carregar a IA
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = "disabled"

# 3. SÓ AGORA importamos as bibliotecas pesadas
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from duckduckgo_search import DDGS

st.title("🎯 Motor SDR Autônomo - Next Tier Up")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")
    
    st.header("🔎 Escolha o Alvo")
    estrategia = st.radio(
        "Fonte de Leads:",
        ["Licitações (PNCP)", "OSINT LinkedIn (Decisores)", "Sniper SDR (Negócios Locais)"]
    )

# --- BOTS DE EXTRAÇÃO ---

def bot_pncp():
    hoje = datetime.now().strftime("%Y%m%d")
    url = f"https://pncp.gov.br/api/consulta/v1/contratos?dataInicial={hoje}&dataFinal={hoje}&pagina=1"
    try:
        resposta = requests.get(url, headers={'accept': 'application/json'}, timeout=15)
        leads = []
        if resposta.status_code == 200:
            for c in resposta.json().get('data', [])[:3]:
                if c.get('niFornecedor'):
                    leads.append({
                        "alvo": c.get('nomeRazaoSocialFornecedor'),
                        "contexto": f"Ganhou licitação hoje para: {c.get('objetoContrato', 'Serviços/Obras')}",
                        "sinal": "Vitória em Licitação Pública"
                    })
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro no Bot do PNCP: {e}")
        return []

def bot_osint_linkedin():
    dork = 'site:br.linkedin.com/in "CEO" OR "Diretor" "Uberlândia"'
    leads = []
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(dork, max_results=3, backend="html"))
            if not resultados:
                st.warning("⚠️ Firewall do buscador bloqueou a raspagem silenciosamente.")
            for r in resultados:
                leads.append({
                    "alvo": r.get('title', '').split('-')[0].strip(),
                    "contexto": f"Resumo: {r.get('body', '')} | Link: {r.get('href', '')}",
                    "sinal": "Mudança de cargo recente ou perfil ativo"
                })
        return leads
    except Exception as e:
        st.error(f"⚠️ Bloqueio no Radar LinkedIn: {e}")
        return []

def bot_sniper_local():
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": "Clínica de Estética em Uberlândia",
        "format": "json",
        "limit": 3,
        "addressdetails": 1
    }
    headers = {"User-Agent": "MotorSDR_NextTierUp_Bot/1.0"}
    
    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=10)
        leads = []
        if resposta.status_code == 200:
            dados = resposta.json()
            for r in dados:
                nome_fantasia = r.get('display_name', '').split(',')[0]
                leads.append({
                    "alvo": nome_fantasia,
                    "contexto": f"Endereço físico confirmado: {r.get('display_name', '')}",
                    "sinal": "Negócio local operando com sede física na região"
                })
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro no Sniper Local (Nominatim): {e}")
        return []

# --- MOTOR PRINCIPAL ---

if st.button("🚀 Iniciar Caçada de Leads"):
    if not chave_api:
        st.error("⚠️ Insira a sua chave do Gemini na barra lateral.")
    else:
        area_processamento = st.container()
        os.environ["GOOGLE_API_KEY"] = chave_api
        
        try:
            motor_gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
            
            agente_dados = Agent(
                role="Analista de OSINT e Inteligência", 
                goal="Analisar os dados raspados da web e traçar um perfil corporativo.", 
                backstory="Expert em inteligência de mercado B2B.", 
                llm=motor_gemini,
                allow_delegation=False
            )
            
            agente_sdr = Agent(
                role="SDR Especialista Omnichannel", 
                goal="Criar cadências de prospecção fria de altíssima conversão.", 
                backstory="Closer de elite. Sua especialidade é a Receita Previsível.", 
                llm=motor_gemini,
                allow_delegation=False
            )
            
            with area_processamento:
                with st.spinner(f"Acordando bots para a estratégia: {estrategia}..."):
                    if estrategia == "Licitações (PNCP)":
                        leads = bot_pncp()
                    elif estrategia == "OSINT LinkedIn (Decisores)":
                        leads = bot_osint_linkedin()
                    else:
                        leads = bot_sniper_local()
                
                if not leads:
                    st.warning("O bot não conseguiu extrair dados no momento.")
                else:
                    st.success(f"🔥 Sistema interceptou {len(leads)} alvos na web!")
                    
                    for lead in leads:
                        with st.container():
                            st.write(f"---")
                            st.write(f"**🎯 Alvo:** {lead['alvo']}")
                            st.write(f"**📡 Sinal Detectado:** {lead['sinal']}")
                            
                            t1 = Task(
                                description=f"Analise o alvo: {lead['alvo']}. Contexto: '{lead['contexto']}'. Sinal: '{lead['sinal']}'. Descreva as dores operacionais e comerciais desse alvo hoje.",
                                expected_output="Análise rápida do perfil e hipótese de dor comercial.",
                                agent=agente_dados
                            )
                            t2 = Task(
                                description=f"Com base no perfil, crie uma cadência de prospecção B2B de 3 passos:\n1) E-mail Frio (usando o sinal {lead['sinal']}).\n2) Mensagem de LinkedIn.\n3) Script de Cold Call.",
                                expected_output="Cadência com 1 E-mail, 1 Mensagem de LinkedIn e 1 Script de Ligação.",
                                agent=agente_sdr
                            )
                            
                            crew = Crew(agents=[agente_dados, agente_sdr], tasks=[t1, t2], process=Process.sequential)
                            
                            try:
                                resultado = crew.kickoff()
                                st.info("✅ Material de Abordagem Gerado:")
                                st.markdown(resultado.raw)
                            except Exception as erro_ia:
                                st.error(f"Erro na IA. Log técnico:")
                                st.code(str(erro_ia))
                        time.sleep(1) 
                        
        except Exception as e:
            st.error(f"Erro crítico: {e}")
