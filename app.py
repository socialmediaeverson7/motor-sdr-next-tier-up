import os
import time
import streamlit as st
from crewai import Agent, Task, Crew, Process

# Configurações de segurança contra erros de infraestrutura
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = "disabled"

st.set_page_config(page_title="Motor SDR - Next Tier Up", page_icon="🚀", layout="wide")
st.title("🎯 Motor SDR Autônomo - Next Tier Up")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")

if st.button("🚀 Iniciar Caçada de Leads"):
    if not chave_api:
        st.error("⚠️ Insira a sua chave do Gemini na barra lateral.")
    else:
        area_processamento = st.container()
        
        # Guardamos a chave na memória para o CrewAI usar automaticamente
        os.environ["GEMINI_API_KEY"] = chave_api
        
        try:
            # A GRANDE MUDANÇA: Passar o LLM como um texto simples
            modelo_gemini = "gemini/gemini-1.5-flash"
            
            agente_dados = Agent(
                role="Analista", 
                goal="Consultar sócios via CNPJ.", 
                backstory="Expert em dados.", 
                llm=modelo_gemini
            )
            
            agente_sdr = Agent(
                role="SDR", 
                goal="Escrever e-mail comercial.", 
                backstory="Closer de elite.", 
                llm=modelo_gemini
            )
            
            with area_processamento:
                with st.spinner("Conectando ao PNCP..."):
                    # Simulação de leads (substitua pela sua função real de busca depois)
                    leads = [{"cnpj": "00000000000191", "empresa": "Exemplo LTDA", "objeto": "Serviço de TI"}]
                
                if not leads:
                    st.warning("Nenhum contrato novo encontrado hoje.")
                else:
                    st.success(f"🔥 Encontrados {len(leads)} leads!")
                    
                    for lead in leads:
                        with st.container():
                            st.write(f"---")
                            st.write(f"**⚙️ Processando:** {lead['empresa']}")
                            
                            t1 = Task(description=f"Consultar {lead['cnpj']}", expected_output="Sócios", agent=agente_dados)
                            t2 = Task(description=f"Escrever e-mail sobre {lead['objeto']}", expected_output="E-mail", agent=agente_sdr)
                            
                            crew = Crew(agents=[agente_dados, agente_sdr], tasks=[t1, t2], process=Process.sequential)
                            resultado = crew.kickoff()
                            
                            st.info("E-mail Gerado:")
                            st.markdown(resultado.raw) # .raw extrai o texto final limpo
                        
                        time.sleep(0.5) 
                        
        except Exception as e:
            st.error(f"Erro no sistema: {e}")
