import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

# Configuração simples para evitar erros de inicialização
st.set_page_config(page_title="Motor SDR", layout="wide")

st.title("🎯 Motor SDR Autônomo")

with st.sidebar:
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")

if st.button("🚀 Iniciar"):
    if not chave_api:
        st.error("Insira a chave API.")
    else:
        try:
            os.environ["GEMINI_API_KEY"] = chave_api
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
            
            # Inicialização mínima para evitar ValidationError
            agente_dados = Agent(
                role="Analista",
                goal="Analisar dados.",
                backstory="Especialista em dados.",
                llm=llm
            )
            
            st.success("Agente inicializado com sucesso!")
            
        except Exception as e:
            st.error(f"Erro ao inicializar: {e}")
