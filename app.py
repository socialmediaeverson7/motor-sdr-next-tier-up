import os
import time
import requests
from datetime import datetime
import streamlit as st
from crewai import Agent, Task, Crew, Process

# Configurações de segurança contra erros de infraestrutura
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = "disabled"

st.set_page_config(page_title="Motor SDR - Next Tier Up", page_icon="🚀", layout="wide")
st.title("🎯 Motor SDR Autônomo - Next Tier Up")
st.markdown("Prospecção B2B baseada em sinais (PNCP) com Cadência Omnichannel.")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")

# --- FUNÇÃO REAL: Busca de contratos vencidos hoje no Portal Nacional ---
def buscar_vencedores_pncp_hoje():
    hoje = datetime.now().strftime("%Y%m%d")
    url = f"https://pncp.gov.br/api/consulta/v1/contratos?dataInicial={hoje}&dataFinal={hoje}&pagina=1"
    headers = {'accept': 'application/json'}
    try:
        resposta = requests.get(url, headers=headers, timeout=15)
        lista_cnpjs = []
        if resposta.status_code == 200:
            dados = resposta.json()
            # Pegamos os 3 primeiros contratos do dia para teste
            for contrato in dados.get('data', [])[:3]: 
                cnpj = contrato.get('niFornecedor')
                nome_empresa = contrato.get('nomeRazaoSocialFornecedor')
                objeto = contrato.get('objetoContrato', 'Serviços/Obras')
                if cnpj and len(str(cnpj)) == 14:
                    lista_cnpjs.append({"cnpj": cnpj, "empresa": nome_empresa, "objeto": objeto})
            return lista_cnpjs
        return []
    except Exception:
        return []

if st.button("🚀 Iniciar Caçada de Leads"):
    if not chave_api:
        st.error("⚠️ Insira a sua chave do Gemini na barra lateral.")
    else:
        area_processamento = st.container()
        os.environ["GEMINI_API_KEY"] = chave_api
        
        try:
            # O nome do modelo
            modelo_gemini = "gemini/gemini-1.5-flash-latest"
            
            agente_dados = Agent(
                role="Analista de Inteligência", 
                goal="Analisar a empresa que ganhou a licitação e traçar um perfil corporativo.", 
                backstory="Você é um expert em inteligência de mercado B2B.", 
                llm=modelo_gemini,
                allow_delegation=False
            )
            
            agente_sdr = Agent(
                role="SDR Especialista Omnichannel", 
                goal="Criar cadências de prospecção fria de alta conversão.", 
                backstory="Você é um Closer de elite na Next Tier Up. Você sabe que depender de um só canal é um erro e usa e-mail, LinkedIn e ligações de forma estratégica.", 
                llm=modelo_gemini,
                allow_delegation=False
            )
            
            with area_processamento:
                with st.spinner("Buscando empresas reais no PNCP..."):
                    leads = buscar_vencedores_pncp_hoje()
                
                if not leads:
                    st.warning("Nenhum contrato novo encontrado hoje no PNCP. Tente novamente mais tarde.")
                else:
                    st.success(f"🔥 Encontrados {len(leads)} leads quentes reais!")
                    
                    for lead in leads:
                        with st.container():
                            st.write(f"---")
                            st.write(f"**🏢 Empresa:** {lead['empresa']} (CNPJ: {lead['cnpj']})")
                            st.write(f"**📜 Contrato ganho:** {lead['objeto'][:100]}...")
                            
                            t1 = Task(
                                description=f"Analise a vitória da empresa {lead['empresa']} (CNPJ: {lead['cnpj']}) que acaba de ganhar um contrato público para: '{lead['objeto']}'. Descreva brevemente o perfil provável do tomador de decisão (CEO/Diretor) desta empresa e as possíveis dores operacionais após ganhar esse contrato.",
                                expected_output="Perfil executivo da empresa e hipótese de dor.",
                                agent=agente_dados
                            )
                            t2 = Task(
                                description=f"Com base no perfil mapeado, crie uma cadência de prospecção B2B de 3 passos para a Next Tier Up abordar o dono da {lead['empresa']}:\n1) E-mail Frio: Curto, parabenizando pelo contrato '{lead['objeto']}' e oferecendo ajuda na operação comercial.\n2) Mensagem de LinkedIn: Curta, apenas para conexão e networking.\n3) Script de Cold Call: Abertura de 30 segundos usando o contrato como gancho.",
                                expected_output="Cadência estruturada com 1 E-mail, 1 Mensagem de LinkedIn e 1 Script de Ligação.",
                                agent=agente_sdr
                            )
                            
                            crew = Crew(agents=[agente_dados, agente_sdr], tasks=[t1, t2], process=Process.sequential)
                            
                            try:
                                resultado = crew.kickoff()
                                st.info("✅ Cadência Omnichannel Gerada:")
                                st.markdown(resultado.raw)
                            except Exception as erro_ia:
                                # Captura e exibe o erro exato do Google/LiteLLM
                                st.error(f"Erro na IA ao processar {lead['empresa']}. Relatório técnico abaixo:")
                                st.code(str(erro_ia))
                        
                        time.sleep(1) 
                        
        except Exception as e:
            st.error(f"Erro fatal no sistema: {e}")
