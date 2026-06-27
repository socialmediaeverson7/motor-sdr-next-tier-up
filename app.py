import os
import requests
import time
from datetime import datetime
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

st.set_page_config(page_title="Motor SDR - Next Tier Up", page_icon="🚀", layout="wide")

st.title("🎯 Motor SDR Autônomo - Next Tier Up")
st.markdown("Prospecção B2B baseada em sinais (Signal-Based Selling) de licitações públicas.")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")
    st.info("Sua chave não é salva. Ela é usada apenas durante a sessão.")

def buscar_vencedores_pncp_hoje():
    hoje = datetime.now().strftime("%Y%m%d")
    url = f"https://pncp.gov.br/api/consulta/v1/contratos?dataInicial={hoje}&dataFinal={hoje}&pagina=1"
    headers = {'accept': 'application/json'}
    resposta = requests.get(url, headers=headers)
    lista_cnpjs = []
    if resposta.status_code == 200:
        dados = resposta.json()
        for contrato in dados.get('data', [])[:3]: 
            cnpj = contrato.get('niFornecedor')
            nome_empresa = contrato.get('nomeRazaoSocialFornecedor')
            objeto = contrato.get('objetoContrato', 'Serviços/Obras')
            if cnpj and len(str(cnpj)) == 14:
                lista_cnpjs.append({"cnpj": cnpj, "empresa": nome_empresa, "objeto": objeto})
        return lista_cnpjs
    return []

@tool("Consulta Oficial Receita Federal")
def consulta_receita(cnpj: str) -> str:
    """Consulta um CNPJ na Receita Federal para descobrir os donos e sócios da empresa."""
    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
    
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        razao = dados.get('razao_social', 'N/A')
        socios = [socio.get('nome_socio').title() for socio in dados.get('qsa', [])]
        socios_str = ", ".join(socios) if socios else "Sócio não informado"
        return f"Empresa: {razao} | Decisores (Donos): {socios_str}"
    return "Erro na busca."

if st.button("🚀 Iniciar Caçada de Leads", use_container_width=True):
    if not chave_api:
        st.error("⚠️ Por favor, insira a sua chave do Gemini na barra lateral antes de começar.")
    else:
        os.environ["GEMINI_API_KEY"] = chave_api
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
                agente_dados = Agent(
            role="Analista de Dados", 
            goal="Consultar o CNPJ na Receita Federal e entregar os sócios.", 
            backstory="Você é preciso.", 
            tools=[consulta_receita], 
            verbose=False, 
            llm=llm,
            allow_delegation=False
        )
        agente_sdr = Agent(
            role="SDR Especialista", 
            goal="Escrever e-mails baseados no contrato vencido.", 
            backstory="Você é um Closer de elite na Next Tier Up. Escreva abordagens diretas.", 
            verbose=False, 
            llm=llm,
            allow_delegation=False
        )
        
        
        with st.spinner("Conectando ao Portal do Governo (PNCP)..."):
            leads = buscar_vencedores_pncp_hoje()
            
        if not leads:
            st.warning("Nenhum contrato novo encontrado hoje no PNCP.")
        else:
            st.success(f"🔥 Encontrados {len(leads)} leads quentes! Acordando Agentes de IA...")
            barra_progresso = st.progress(0)
            
            for indice, lead in enumerate(leads):
                with st.expander(f"⚙️ Processando: {lead['empresa']}", expanded=True):
                    st.write(f"**Contrato Vencido:** {lead['objeto']}")
                    
                    tarefa_investigacao = Task(description=f"Consulte o CNPJ {lead['cnpj']} na Receita. Identifique os sócios.", expected_output="Nome dos sócios.", agent=agente_dados)
                    tarefa_venda = Task(description=f"Escreva um e-mail para o Sócio sobre a vitória neste contrato: '{lead['objeto']}'.", expected_output="E-mail comercial.", agent=agente_sdr)
                    
                    equipe = Crew(agents=[agente_dados, agente_sdr], tasks=[tarefa_investigacao, tarefa_venda], process=Process.sequential)
                    resultado = equipe.kickoff()
                    
                    st.info("E-mail Gerado com Sucesso:")
                    st.markdown(resultado)
                
                barra_progresso.progress((indice + 1) / len(leads))
                time.sleep(2)
                
            st.balloons()
            st.success("✅ Prospecção Finalizada!")
          
