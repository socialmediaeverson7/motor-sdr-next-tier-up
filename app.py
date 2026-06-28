import sys
import types
import os
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st

# 1. A REGRA DE OURO DO STREAMLIT
st.set_page_config(page_title="Motor SDR - Next Tier Up", page_icon="🎯", layout="wide")

# 2. O MÓDULO FANTASMA (Bypass)
if "pkg_resources" not in sys.modules:
    mock_pkg = types.ModuleType("pkg_resources")
    mock_pkg.get_distribution = lambda x: types.SimpleNamespace(version="0.0.0")
    sys.modules["pkg_resources"] = mock_pkg

# 3. SEGURANÇA
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = "disabled"

# 4. BIBLIOTECAS DE IA
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

st.title("🎯 Motor SDR Autônomo - Next Tier Up")

with st.sidebar:
    st.header("⚙️ Chave de IA")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")
    
    st.header("✉️ Credenciais de Disparo (Canal 1)")
    remetente_email = st.text_input("Seu E-mail (Gmail/Workspace):", placeholder="seuemail@gmail.com")
    remetente_senha = st.text_input("Senha de App (Google):", type="password", help="Use uma 'Senha de App' gerada na segurança do Google, não sua senha normal.")
    
    st.header("🔎 Arsenal de Prospecção")
    estrategia = st.radio(
        "Selecione o Motor:",
        [
            "1. Radar de Licitações (Automático)", 
            "2. Sniper B2B de Nicho (Automático)", 
            "3. Raio-X de CNPJ (Manual)"
        ]
    )
    
    termo_busca = ""
    cnpj_alvo = ""
    
    if estrategia == "2. Sniper B2B de Nicho (Automático)":
        termo_busca = st.text_input("Qual nicho e região?", value="Transportadora em Uberlândia")
    elif estrategia == "3. Raio-X de CNPJ (Manual)":
        cnpj_alvo = st.text_input("Digite o CNPJ (somente números):")

# --- BOTS DE EXTRAÇÃO ---

def bot_pncp():
    hoje = datetime.now().strftime("%Y%m%d")
    url = f"https://pncp.gov.br/api/consulta/v1/contratos?dataInicial={hoje}&dataFinal={hoje}&pagina=1"
    try:
        resposta = requests.get(url, headers={'accept': 'application/json'}, timeout=15)
        leads = []
        if resposta.status_code == 200:
            for c in resposta.json().get('data', [])[:10]: # Acelerador em 10!
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
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": termo, "format": "json", "limit": 10, "addressdetails": 1}
    headers = {"User-Agent": "MotorSDR_NextTierUp_Bot/2.0"}
    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=10)
        leads = []
        if resposta.status_code == 200:
            dados = resposta.json()
            for r in dados:
                leads.append({
                    "alvo": r.get('display_name', '').split(',')[0],
                    "contexto": f"Endereço: {r.get('display_name', '')}",
                    "sinal": f"Operação comercial ativa confirmada."
                })
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro no mapa: {e}")
        return []

def bot_osint_receita(cnpj):
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14: return []
    url = f"https://receitaws.com.br/v1/cnpj/{cnpj_limpo}"
    try:
        resposta = requests.get(url, timeout=15)
        leads = []
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("status") == "ERROR": return []
            socios = [s.get('nome') for s in dados.get('qsa', [])]
            leads.append({
                "alvo": dados.get('nome'),
                "contexto": f"Capital: R$ {dados.get('capital_social')}. Atividade: {dados.get('atividade_principal', [{}])[0].get('text', '')}. Sócios: {', '.join(socios)}",
                "sinal": "Análise Estratégica Societária"
            })
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro CNPJ: {e}")
        return []

# --- MOTOR PRINCIPAL E EXECUÇÃO ---

if st.button("🚀 Iniciar Caçada e Gerar Cadências"):
    if not chave_api:
        st.error("⚠️ Insira a chave do Gemini.")
        st.stop()
        
    area_processamento = st.container()
    os.environ["GOOGLE_API_KEY"] = chave_api
    
    try:
        motor_gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        agente_dados = Agent(
            role="Analista de Inteligência", 
            goal="Analisar a empresa alvo.", 
            backstory="Expert B2B que acha dores operacionais.", 
            llm=motor_gemini, allow_delegation=False
        )
        
        agente_sdr = Agent(
            role="SDR", 
            goal="Escrever e-mail curto e agressivo focado em conversão.", 
            backstory="Closer de elite focado em Receita Previsível.", 
            llm=motor_gemini, allow_delegation=False
        )
        
        with area_processamento:
            with st.spinner("Extraindo alvos..."):
                if estrategia == "1. Radar de Licitações (Automático)": leads = bot_pncp()
                elif estrategia == "2. Sniper B2B de Nicho (Automático)": leads = bot_sniper_nicho(termo_busca)
                else: leads = bot_osint_receita(cnpj_alvo)
            
            if not leads:
                st.warning("Nenhum alvo encontrado.")
            else:
                st.success(f"🔥 {len(leads)} alvos interceptados! Iniciando IA...")
                
                for idx, lead in enumerate(leads):
                    with st.expander(f"🎯 Alvo: {lead['alvo']}", expanded=True):
                        st.write(f"**Sinal:** {lead['contexto']}")
                        
                        t1 = Task(description=f"Analise: {lead['alvo']}. Contexto: {lead['contexto']}.", expected_output="Dor mapeada.", agent=agente_dados)
                        t2 = Task(description=f"Crie um E-mail de Prospecção Fria para a Next Tier Up fechar com {lead['alvo']}. Apenas o texto do e-mail.", expected_output="Texto do E-mail.", agent=agente_sdr)
                        
                        crew = Crew(agents=[agente_dados, agente_sdr], tasks=[t1, t2], process=Process.sequential)
                        
                        try:
                            # Converte o objeto da IA garantindo que seja string!
                            copy_gerada = str(crew.kickoff())
                            
                            # PAINEL OMNICHANNEL
                            aba_email, aba_linkedin = st.tabs(["✉️ Disparador (Canal 1)", "💼 Próximos Canais"])
                            
                            with aba_email:
                                dest = st.text_input("E-mail do Lead:", key=f"dest_{idx}")
                                assunto = st.text_input("Assunto do E-mail:", value=f"Estratégia para {lead['alvo']}", key=f"ass_{idx}")
                                corpo_email = st.text_area("Edite a Copy Gerada:", value=copy_gerada, height=250, key=f"copy_{idx}")
                                
                                if st.button("🚀 Disparar E-mail Frio", key=f"btn_{idx}"):
                                    if not remetente_email or not remetente_senha:
                                        st.error("Preencha seu E-mail e Senha de App na barra lateral!")
                                    elif not dest:
                                        st.error("Preencha o e-mail de destino.")
                                    else:
                                        try:
                                            # Construindo o pacote do E-mail
                                            msg = MIMEMultipart()
                                            msg['From'] = remetente_email
                                            msg['To'] = dest
                                            msg['Subject'] = assunto
                                            msg.attach(MIMEText(corpo_email, 'plain'))
                                            
                                            # Conectando no servidor do Google e disparando
                                            server = smtplib.SMTP('smtp.gmail.com', 587)
                                            server.starttls()
                                            server.login(remetente_email, remetente_senha)
                                            server.send_message(msg)
                                            server.quit()
                                            st.success(f"Vitória! E-mail disparado para {dest} 🎯")
                                        except Exception as err:
                                            st.error(f"Erro no servidor SMTP: {err}")
                                            
                            with aba_linkedin:
                                st.info("Em breve: Botões de conexão direta para o LinkedIn e Scripts de Ligação.")
                                
                        except Exception as erro_ia:
                            st.error(f"Erro na IA: {erro_ia}")
                    time.sleep(1)
                    
    except Exception as e:
        st.error(f"Erro crítico no motor de IA: {e}")
