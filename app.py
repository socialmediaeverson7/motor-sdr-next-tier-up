import os
import requests
import time
from datetime import datetime
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

# Desativa rastreamento pesado que causa erros
os.environ["LANGCHAIN_TRACING_V2"] = "false"

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
            
            agente_dados = Agent(
                role="Analista",
                goal="Analisar dados.",
                backstory="Especialista em dados.",
                llm=llm
            )
            
            st.success("Motor Online!")
            
        except Exception as e:
            st.error(f"Erro: {e}")
