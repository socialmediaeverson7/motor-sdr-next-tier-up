# 1. PRIMEIRO: Importamos apenas as bibliotecas nativas do sistema
import os
import sys
import types

# 2. SEGUNDO: Fazemos a injeção do fantasma na memória (O Bypass)
if "pkg_resources" not in sys.modules:
    mock_pkg = types.ModuleType("pkg_resources")
    mock_pkg.get_distribution = lambda x: types.SimpleNamespace(version="0.0.0")
    sys.modules["pkg_resources"] = mock_pkg

# 3. TERCEIRO: Desligamos os rastreadores
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = "disabled"

# 4. QUARTO: SÓ AGORA importamos as bibliotecas pesadas!
import time
import requests
from datetime import datetime
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from duckduckgo_search import DDGS

# --- INÍCIO DA INTERFACE ---

st.set_page_config(page_title="Motor SDR - Next Tier Up", page_icon="🎯", layout="wide")
st.title("🎯 Motor SDR Autônomo - Next Tier Up")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")
    
    st.header("🔎 Escolha o Alvo")
    estrategia = st.radio(
        "Fonte de Leads:",
        ["Licitações (PNCP)", "OSINT LinkedIn (Decisores)", "Sniper SDR (Negócios Locais)"]
    )

# --- BOTS DE EXTRAÇÃO (SEM CUSTO DE API) ---

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
            resultados = ddgs.text(dork, max_results=3)
            for r in resultados:
                leads.append({
                    "alvo": r.get('title', '').split('-')[0].strip(),
                    "contexto": f"Resumo do perfil: {r.get('body', '')} | Link: {r.get('href', '')}",
                    "sinal": "Mudança de cargo recente ou perfil ativo"
                })
        return leads
    except Exception as e:
        # AQUI O ERRO REAL SERÁ EXPOSTO
        st.error(f"⚠️ Bloqueio no Radar LinkedIn (DDGS): {e}")
        return []

def bot_sniper_local():
    termo_busca = 'Clínicas de Estética em Uberlândia'
    leads = []
    try:
        with DDGS() as ddgs:
            resultados = ddgs.text(termo_busca, max_results=3)
            for r in resultados:
                leads.append({
                    "alvo": r.get('title', ''),
                    "contexto": f"Descrição web: {r.get('body', '')} | Site: {r.get('href', '')}",
                    "sinal": "Negócio local ativo com presença digital"
                })
        return leads
    except Exception as e:
        # AQUI O ERRO REAL SERÁ EXPOSTO
        st.error(f"⚠️ Bloqueio no Sniper Local (DDGS): {e}")
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
                goal="Analisar os dados raspados da web e traçar um perfil psicológico e corporativo do alvo.", 
                backstory="Você é um expert em inteligência de mercado B2B e engenharia social. Você encontra dores que as empresas nem sabem que têm.", 
                llm=motor_gemini,
                allow_delegation=False
            )
            
            agente_sdr = Agent(
                role="SDR Especialista Omnichannel", 
                goal="Criar cadências de prospecção fria de altíssima conversão.", 
                backstory="Você é um Closer de elite na Next Tier Up. Sua especialidade é a Receita Previsível. Você nunca é invasivo, sempre gera valor no primeiro contato.", 
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
                    st.warning("O bot não conseguiu extrair dados no momento. Verifique os erros acima.")
                else:
                    st.success(f"🔥 Sistema interceptou {len(leads)} alvos na web!")
                    
                    for lead in leads:
                        with st.container():
                            st.write(f"---")
                            st.write(f"**🎯 Alvo:** {lead['alvo']}")
                            st.write(f"**📡 Sinal Detectado:** {lead['sinal']}")
                            
                            t1 = Task(
                                description=f"Analise o seguinte alvo extraído da web: {lead['alvo']}. O contexto encontrado foi: '{lead['contexto']}'. O sinal de compra é: '{lead['sinal']}'. Descreva as possíveis dores operacionais e comerciais desse alvo hoje.",
                                expected_output="Análise rápida do perfil e hipótese de dor comercial.",
                                agent=agente_dados
                            )
                            t2 = Task(
                                description=f"Com base no perfil mapeado, crie uma cadência de prospecção B2B de 3 passos para a Next Tier Up abordar {lead['alvo']}:\n1) E-mail Frio: Usando o sinal de compra ({lead['sinal']}) como gancho.\n2) Mensagem de LinkedIn: Curta, para networking.\n3) Script de Cold Call: Abertura de 30 segundos usando o contexto mapeado.",
                                expected_output="Cadência com 1 E-mail, 1 Mensagem de LinkedIn e 1 Script de Ligação (sem jargões).",
                                agent=agente_sdr
                            )
                            
                            crew = Crew(agents=[agente_dados, agente_sdr], tasks=[t1, t2], process=Process.sequential)
                            
                            try:
                                resultado = crew.kickoff()
                                st.info("✅ Material de Abordagem Gerado:")
                                st.markdown(resultado.raw)
                            except Exception as erro_ia:
                                st.error(f"Erro na IA ao processar {lead['alvo']}. Log técnico:")
                                st.code(str(erro_ia))
                        
                        time.sleep(1) 
                        
        except Exception as e:
            st.error(f"Erro crítico: {e}")
