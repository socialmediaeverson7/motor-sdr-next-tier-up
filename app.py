import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

# Impede erros de validação do LangChain/LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = "disabled"

st.set_page_config(page_title="Motor SDR - Next Tier Up", page_icon="🚀", layout="wide")

st.title("🎯 Motor SDR Autônomo - Next Tier Up")
st.markdown("Prospecção B2B com IA integrada.")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")

if st.button("🚀 Iniciar Motor de Prospecção"):
    if not chave_api:
        st.error("⚠️ Insira a sua chave API do Gemini na barra lateral.")
    else:
        try:
            os.environ["GEMINI_API_KEY"] = chave_api
            # Instanciando o modelo
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
            
            # Agentes definidos de forma simples para evitar Pydantic ValidationError
            agente_dados = Agent(
                role="Analista de Dados",
                goal="Identificar sócios através do CNPJ.",
                backstory="Especialista em inteligência de mercado.",
                llm=llm
            )
            
            agente_sdr = Agent(
                role="SDR Especialista",
                goal="Elaborar e-mails comerciais de alto impacto.",
                backstory="Closer de elite focado em vendas B2B.",
                llm=llm
            )
            
            # Exemplo de fluxo
            st.success("✅ Motores iniciados com sucesso!")
            st.info("O sistema está pronto para processar os dados.")
            
        except Exception as e:
            st.error(f"Erro crítico na inicialização do sistema: {e}")
            st.write("Verifique se as bibliotecas no requirements.txt estão na versão correta.")
