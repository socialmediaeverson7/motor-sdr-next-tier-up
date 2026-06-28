"""
Módulo de Agentes de IA
Implementa os agentes CrewAI para análise e geração de cadências
"""

import os
import streamlit as st
from typing import List, Optional
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import ScrapeWebsiteTool
from config.settings import DEFAULT_LLM_MODEL, LLM_TEMPERATURE, AGENT_PROMPTS, TASK_TEMPLATES, MESSAGES

class AIAgentError(Exception):
    """Exceção customizada para erros nos agentes de IA"""
    pass

class AIAgentManager:
    """
    Gerenciador de agentes de IA
    Responsável por criar, configurar e executar agentes CrewAI
    """
    
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise AIAgentError("Chave de API do Gemini não fornecida")
        
        try:
            clean_api_key = api_key.strip()
            os.environ["GOOGLE_API_KEY"] = clean_api_key
            
            # Inicialização explícita do modelo
            self.llm = ChatGoogleGenerativeAI(
                model=DEFAULT_LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                google_api_key=clean_api_key
            )
        except Exception as e:
            raise AIAgentError(f"Erro ao inicializar modelo de IA: {e}")
    
    def create_data_analyst_agent(self) -> Agent:
        config = AGENT_PROMPTS["data_analyst"]
        
        # Inicializa a ferramenta de raspagem
        scrape_tool = ScrapeWebsiteTool()
        
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm,
            tools=[scrape_tool],
            allow_delegation=False,
            verbose=True
        )
    
    def create_sdr_agent(self) -> Agent:
        config = AGENT_PROMPTS["sdr"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )
    
    def create_analysis_task(self, agent: Agent, batch_text: str) -> Task:
        template = TASK_TEMPLATES["analysis"]
        description = template["description"].format(batch_text=batch_text)
        
        return Task(
            description=description,
            expected_output=template["expected_output"],
            agent=agent
        )
    
    def create_cadence_task(self, agent: Agent) -> Task:
        template = TASK_TEMPLATES["cadence"]
        return Task(
            description=template["description"],
            expected_output=template["expected_output"],
            agent=agent
        )
    
    def execute_crew(self, agents: List[Agent], tasks: List[Task]) -> str:
        try:
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            # Tratamento de erro detalhado para facilitar depuração
            raise AIAgentError(f"Erro na execução da crew: {str(e)}")
    
    def process_batch(self, batch_text: str) -> str:
        try:
            data_analyst = self.create_data_analyst_agent()
            sdr_agent = self.create_sdr_agent()
            
            analysis_task = self.create_analysis_task(data_analyst, batch_text)
            cadence_task = self.create_cadence_task(sdr_agent)
            
            return self.execute_crew(
                agents=[data_analyst, sdr_agent],
                tasks=[analysis_task, cadence_task]
            )
        except Exception as e:
            raise AIAgentError(f"Erro crítico no processamento em lote: {e}")

def validate_and_initialize_ai(api_key: str) -> Optional[AIAgentManager]:
    try:
        if not api_key or not api_key.strip():
            st.error(MESSAGES["error_api_key"])
            return None
        return AIAgentManager(api_key)
    except AIAgentError as e:
        st.error(f"Erro na inicialização da IA: {e}")
        return None
