import sys
import types
import os
import time
import requests
from datetime import datetime
import streamlit as st

# 1. A REGRA DE OURO DO STREAMLIT
st.set_page_config(page_title="Motor SDR - Next Tier Up", page_icon="🎯", layout="wide")

# 2. O MÓDULO FANTASMA (Bypass)
if "pkg_resources" not in sys.modules:
    mock_pkg = types.ModuleType("pkg_resources")
    mock_pkg.get_distribution = lambda x: types.SimpleNamespace(version="0.0.0")
    sys.modules["pkg_resources"] = mock_pkg

# 3. SEGURANÇA CONTRA RASTREAMENTO
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = "disabled"

# 4. BIBLIOTECAS DE IA
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

st.title("🎯 Motor SDR Autônomo - Next Tier Up")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")
    
    st.header("🔎 Arsenal de Prospecção")
    estrategia = st.radio(
        "Selecione o Motor:",
        [
            "1. Radar de Licitações (Automático)", 
            "2. Sniper B2B de Nicho (Automático)", 
            "3. Raio-X de CNPJ (Manual)"
        ]
    )
    
    # Controles Dinâmicos baseados na escolha
    termo_busca = ""
    cnpj_alvo = ""
    
    if estrategia == "2. Sniper B2B de Nicho (Automático)":
        st.markdown("O robô vai rastrear empresas ativas por geolocalização.")
        termo_busca = st.text_input("Qual nicho e região?", value="Transportadora em Uberlândia")
        
    elif estrategia == "3. Raio-X de CNPJ (Manual)":
        st.markdown("Enriquecimento profundo para um alvo específico.")
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

def bot_sniper_nicho(termo):
    # API Imune a bloqueios de nuvem que pesquisa empresas reais no mapa
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": termo,
        "format": "json",
        "limit": 3,
        "addressdetails": 1
    }
    headers = {"User-Agent": "MotorSDR_NextTierUp_Bot/2.0"}
    
    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=10)
        leads = []
        if resposta.status_code == 200:
            dados = resposta.json()
            for r in dados:
                nome_fantasia = r.get('display_name', '').split(',')[0]
                endereco_completo = r.get('display_name', '')
                leads.append({
                    "alvo": nome_fantasia,
                    "contexto": f"Empresa localizada via satélite no endereço: {endereco_completo}",
                    "sinal": f"Operação comercial ativa confirmada para o nicho alvo."
                })
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro no rastreamento de mapa: {e}")
        return []

def bot_osint_receita(cnpj):
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
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

# --- MOTOR PRINCIPAL ---

if st.button("🚀 Iniciar Caçada de Leads"):
    # Validações de entrada
    if not chave_api:
        st.error("⚠️ Insira a sua chave do Gemini na barra lateral.")
        st.stop()
    if estrategia == "2. Sniper B2B de Nicho (Automático)" and not termo_busca:
        st.error("⚠️ Digite um nicho e região para o Sniper caçar.")
        st.stop()
    if estrategia == "3. Raio-X de CNPJ (Manual)" and not cnpj_alvo:
        st.error("⚠️ Digite um CNPJ válido para prosseguir.")
        st.stop()

    area_processamento = st.container()
    os.environ["GOOGLE_API_KEY"] = chave_api
    
    try:
        motor_gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        agente_dados = Agent(
            role="Analista de Inteligência Operacional", 
            goal="Analisar a empresa alvo e descobrir as principais dores do seu setor.", 
            backstory="Expert em inteligência de mercado B2B. Você deduz os gargalos comerciais da empresa com base no seu nicho e localização.", 
            llm=motor_gemini,
            allow_delegation=False
        )
        
        agente_sdr = Agent(
            role="SDR Especialista Omnichannel", 
            goal="Criar cadências de prospecção fria de altíssima conversão.", 
            backstory="Closer de elite. Você usa os dados levantados para criar uma abordagem hiper-personalizada que chama a atenção do decisor.", 
            llm=motor_gemini,
            allow_delegation=False
        )
        
        with area_processamento:
            with st.spinner(f"Executando operação: {estrategia}..."):
                if estrategia == "1. Radar de Licitações (Automático)":
                    leads = bot_pncp()
                elif estrategia == "2. Sniper B2B de Nicho (Automático)":
                    leads = bot_sniper_nicho(termo_busca)
                else:
                    leads = bot_osint_receita(cnpj_alvo)
            
            if not leads:
                st.warning("O robô não encontrou resultados para esses parâmetros.")
            else:
                st.success(f"🔥 Sistema interceptou {len(leads)} alvos com sucesso!")
                
                for lead in leads:
                    with st.container():
                        st.write(f"---")
                        st.write(f"**🎯 Alvo:** {lead['alvo']}")
                        st.write(f"**📡 Dados Coletados:** {lead['contexto']}")
                        
                        t1 = Task(
                            description=f"Analise o alvo: {lead['alvo']}. Contexto: '{lead['contexto']}'. Descreva as dores operacionais e comerciais que uma empresa com essas características enfrenta hoje.",
                            expected_output="Análise do perfil da empresa e principais gargalos comerciais.",
                            agent=agente_dados
                        )
                        t2 = Task(
                            description=f"Com base na análise, crie uma cadência de prospecção B2B de 3 passos para a Next Tier Up fechar negócio com {lead['alvo']}:\n1) E-mail Frio.\n2) Mensagem de LinkedIn.\n3) Script de Cold Call de 30s.",
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
        st.error(f"Erro crítico no motor de IA: {e}")
