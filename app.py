import sys
import types
import os
import time
import requests
from datetime import datetime
import streamlit as st

# 1. A REGRA DE OURO DO STREAMLIT
st.set_page_config(page_title="Motor SDR - Next Tier Up", page_icon="🎯", layout="wide")

# 2. O MÓDULO FANTASMA
if "pkg_resources" not in sys.modules:
    mock_pkg = types.ModuleType("pkg_resources")
    mock_pkg.get_distribution = lambda x: types.SimpleNamespace(version="0.0.0")
    sys.modules["pkg_resources"] = mock_pkg

# 3. SEGURANÇA
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = "disabled"

# 4. BIBLIOTECAS PESADAS
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

st.title("🎯 Motor SDR Autônomo - Next Tier Up")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")
    
    st.header("🔎 Escolha o Alvo")
    estrategia = st.radio(
        "Fonte de Leads:",
        ["Licitações (PNCP)", "OSINT Profundo (Raio-X de CNPJ)", "Sniper SDR (Negócios Locais)"]
    )
    
    # Campo dinâmico: Só aparece se a opção de CNPJ for escolhida
    cnpj_alvo = ""
    if estrategia == "OSINT Profundo (Raio-X de CNPJ)":
        cnpj_alvo = st.text_input("Digite o CNPJ (somente números):")

# --- BOTS DE EXTRAÇÃO (100% REST APIs Blindadas) ---

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

def bot_osint_receita(cnpj):
    # Remove pontuações do CNPJ
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        st.warning("⚠️ O CNPJ deve conter 14 números.")
        return []
        
    url = f"https://receitaws.com.br/v1/cnpj/{cnpj_limpo}"
    try:
        resposta = requests.get(url, timeout=15)
        leads = []
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("status") == "ERROR":
                st.warning(f"⚠️ {dados.get('message')}")
                return []
                
            # Extraindo Quadro de Sócios (QSA)
            socios = [s.get('nome') for s in dados.get('qsa', [])]
            socios_str = ", ".join(socios) if socios else "Não listado"
            
            leads.append({
                "alvo": dados.get('nome'),
                "contexto": f"Abertura: {dados.get('abertura')}. Capital Social: R$ {dados.get('capital_social')}. Atividade: {dados.get('atividade_principal', [{}])[0].get('text', '')}. Sócios: {socios_str}.",
                "sinal": "Análise Estratégica Baseada em Maturidade e Estrutura Societária"
            })
        elif resposta.status_code == 429:
            st.warning("⚠️ Limite de consultas da ReceitaWS atingido. Tente em 1 minuto.")
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro na consulta de CNPJ: {e}")
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
    elif estrategia == "OSINT Profundo (Raio-X de CNPJ)" and not cnpj_alvo:
        st.error("⚠️ Digite um CNPJ válido na barra lateral para prosseguir.")
    else:
        area_processamento = st.container()
        os.environ["GOOGLE_API_KEY"] = chave_api
        
        try:
            motor_gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
            
            agente_dados = Agent(
                role="Analista de OSINT e Inteligência", 
                goal="Analisar os dados estruturados e traçar um perfil corporativo/financeiro.", 
                backstory="Expert em inteligência de mercado B2B. Você cruza dados de idade da empresa e capital social para deduzir o nível de maturidade da operação comercial.", 
                llm=motor_gemini,
                allow_delegation=False
            )
            
            agente_sdr = Agent(
                role="SDR Especialista Omnichannel", 
                goal="Criar cadências de prospecção fria de altíssima conversão.", 
                backstory="Closer de elite. Você usa os dados levantados pelo analista (como o nome dos sócios e o tamanho da empresa) para criar abordagens que parecem terem sido escritas por um consultor que estudou a empresa por horas.", 
                llm=motor_gemini,
                allow_delegation=False
            )
            
            with area_processamento:
                with st.spinner(f"Executando operação: {estrategia}..."):
                    if estrategia == "Licitações (PNCP)":
                        leads = bot_pncp()
                    elif estrategia == "OSINT Profundo (Raio-X de CNPJ)":
                        leads = bot_osint_receita(cnpj_alvo)
                    else:
                        leads = bot_sniper_local()
                
                if not leads:
                    st.warning("Nenhum dado extraído.")
                else:
                    st.success(f"🔥 Sistema interceptou o alvo com sucesso!")
                    
                    for lead in leads:
                        with st.container():
                            st.write(f"---")
                            st.write(f"**🎯 Alvo:** {lead['alvo']}")
                            st.write(f"**📡 Dados Coletados:** {lead['contexto']}")
                            
                            t1 = Task(
                                description=f"Analise o alvo: {lead['alvo']}. Contexto: '{lead['contexto']}'. Descreva as dores operacionais e comerciais que uma empresa com essas características (idade, capital, nicho) provavelmente enfrenta hoje.",
                                expected_output="Análise rápida do perfil e hipótese de dor comercial.",
                                agent=agente_dados
                            )
                            t2 = Task(
                                description=f"Com base no perfil, crie uma cadência de prospecção B2B de 3 passos para a Next Tier Up:\n1) E-mail Frio (mencione estrategicamente algum dado do contexto, como o tempo de mercado ou área de atuação, e se direcionando aos sócios se houver).\n2) Mensagem de LinkedIn.\n3) Script de Cold Call.",
                                expected_output="Cadência estruturada contendo E-mail, Mensagem de LinkedIn e Script de Ligação.",
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
