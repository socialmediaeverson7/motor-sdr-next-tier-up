import sys
import types
import os
import requests
import smtplib
import urllib.parse
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

st.title("🎯 Motor SDR Autônomo - Next Tier Up (Modo Batching)")

with st.sidebar:
    st.header("⚙️ Chave de IA")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")
    
    st.header("✉️ Credenciais de Disparo (Canal 1)")
    remetente_email = st.text_input("Seu E-mail (Gmail/Workspace):", placeholder="seuemail@gmail.com")
    remetente_senha = st.text_input("Senha de App (Google):", type="password")
    
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
            for c in resposta.json().get('data', [])[:10]: 
                if c.get('niFornecedor'):
                    leads.append({
                        "alvo": c.get('nomeRazaoSocialFornecedor'),
                        "contexto": f"Ganhou licitação para: {c.get('objetoContrato', 'Serviços/Obras')}"
                    })
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro no Bot do PNCP: {e}")
        return []

def bot_sniper_nicho(termo):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": termo, "format": "json", "limit": 10, "addressdetails": 1}
    headers = {"User-Agent": "MotorSDR_NextTierUp_Bot/3.0"}
    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=10)
        leads = []
        if resposta.status_code == 200:
            for r in resposta.json():
                leads.append({
                    "alvo": r.get('display_name', '').split(',')[0],
                    "contexto": f"Endereço: {r.get('display_name', '')}"
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
                "contexto": f"Capital: R$ {dados.get('capital_social')}. Sócios: {', '.join(socios)}"
            })
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro CNPJ: {e}")
        return []

# --- MOTOR PRINCIPAL E EXECUÇÃO (LOTE) ---

if st.button("🚀 Iniciar Caçada em Lote"):
    if not chave_api:
        st.error("⚠️ Insira a chave do Gemini.")
        st.stop()
        
    area_processamento = st.container()
    os.environ["GOOGLE_API_KEY"] = chave_api
    
    try:
        motor_gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        agente_dados = Agent(
            role="Analista de Inteligência Operacional", 
            goal="Analisar um lote de empresas de uma só vez.", 
            backstory="Você processa listas brutas de prospecção.", 
            llm=motor_gemini, allow_delegation=False
        )
        
        agente_sdr = Agent(
            role="SDR de Alta Escala", 
            goal="Gerar cadências omnichannel rápidas para uma lista de empresas.", 
            backstory="Você cria abordagens curtas e agressivas focadas em conversão. Para cada empresa da lista, gere os blocos: [E-MAIL], [LINKEDIN] e [CALL].", 
            llm=motor_gemini, allow_delegation=False
        )
        
        with area_processamento:
            with st.spinner("Extraindo lote de alvos..."):
                if estrategia == "1. Radar de Licitações (Automático)": leads = bot_pncp()
                elif estrategia == "2. Sniper B2B de Nicho (Automático)": leads = bot_sniper_nicho(termo_busca)
                else: leads = bot_osint_receita(cnpj_alvo)
            
            if not leads:
                st.warning("Nenhum alvo encontrado.")
            else:
                st.success(f"🔥 Lote de {len(leads)} alvos montado. Injetando no Cérebro da IA...")
                
                # EMPACOTAMENTO DOS DADOS
                lote_texto = "\n".join([f"- Empresa: {l['alvo']} | Dados: {l['contexto']}" for l in leads])
                
                t1 = Task(
                    description=f"Leia a seguinte lista de empresas extraídas da web:\n{lote_texto}\n\nFaça um resumo rápido da dor comercial de cada uma.", 
                    expected_output="Análise em lote.", 
                    agent=agente_dados
                )
                t2 = Task(
                    description="Com base na análise do lote, crie uma cadência para CADA empresa da lista. Formate a resposta claramente separando as empresas e os canais de comunicação.", 
                    expected_output="Relatório Mestre de Prospecção.", 
                    agent=agente_sdr
                )
                
                crew = Crew(agents=[agente_dados, agente_sdr], tasks=[t1, t2], process=Process.sequential)
                
                with st.spinner("Processando cadências em paralelo (Batching)..."):
                    try:
                        copy_gerada = str(crew.kickoff())
                        
                        st.markdown("### 🧠 Relatório Mestre de Prospecção")
                        st.info("Aqui estão todas as estratégias geradas em um único fluxo. Use o terminal abaixo para executar.")
                        st.markdown(copy_gerada)
                        
                    except Exception as erro_ia:
                        st.error(f"Erro na IA: {erro_ia}")

# --- TERMINAL DE DISPARO GLOBAL ---
st.markdown("---")
st.markdown("### ⚡ Terminal de Execução Global")
aba_email, aba_wpp, aba_linkedin = st.tabs(["✉️ Disparo de E-mail", "📱 WhatsApp Automático", "💼 Busca Rápida LinkedIn"])

with aba_email:
    dest_global = st.text_input("E-mail do Alvo:")
    assunto_global = st.text_input("Assunto do E-mail:")
    corpo_global = st.text_area("Cole a Copy Gerada no Relatório Acima:", height=150)
    
    if st.button("🚀 Disparar E-mail"):
        if not remetente_email or not remetente_senha:
            st.error("Preencha seu E-mail e Senha de App na barra lateral!")
        elif not dest_global:
            st.error("Preencha o e-mail de destino.")
        else:
            try:
                msg = MIMEMultipart()
                msg['From'] = remetente_email
                msg['To'] = dest_global
                msg['Subject'] = assunto_global
                msg.attach(MIMEText(corpo_global, 'plain'))
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(remetente_email, remetente_senha)
                server.send_message(msg)
                server.quit()
                st.success(f"Vitória! E-mail disparado para {dest_global} 🎯")
            except Exception as err:
                st.error(f"Erro no servidor SMTP: {err}")

with aba_wpp:
    telefone_global = st.text_input("WhatsApp (Ex: 5534999999999):")
    wpp_msg_global = st.text_area("Cole a copy de WhatsApp/Call:")
    
    if telefone_global:
        msg_codificada = urllib.parse.quote(wpp_msg_global)
        st.markdown(f"👉 **[ABRIR WHATSAPP WEB COM A MENSAGEM]({f'https://wa.me/{telefone_global}?text={msg_codificada}'})**")

with aba_linkedin:
    empresa_alvo = st.text_input("Digite o nome da Empresa para buscar os decisores:")
    if empresa_alvo:
        query_linkedin = f"CEO OR Diretor OR Sócio {urllib.parse.quote(empresa_alvo)}"
        link_linkedin = f"https://www.linkedin.com/search/results/people/?keywords={query_linkedin}"
        st.markdown(f"👉 **[PESQUISAR DECISORES NO LINKEDIN]({link_linkedin})**")
