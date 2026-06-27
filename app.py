import os
# Desativar telemetria ANTES de qualquer import do crewai
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
# Importamos apenas o essencial
from crewai import Agent, Task, Crew, Process

st.set_page_config(page_title="Motor SDR", layout="wide")
st.title("🎯 Motor SDR Autônomo")

with st.sidebar:
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")

if st.button("🚀 Iniciar"):
    if not chave_api:
        st.error("Insira a chave API.")
    else:
        os.environ["GEMINI_API_KEY"] = chave_api
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        # Agente simples
        agente = Agent(
            role="Analista",
            goal="Processar dados.",
            backstory="Especialista.",
            llm=llm
        )
        st.success("Motor Rodando!")
