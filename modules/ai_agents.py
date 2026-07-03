"""
Módulo de Agentes de IA
Implementa os agentes CrewAI focados no uso do Ollama Local
"""

import os
import streamlit as st
import requests
from typing import Tuple, Optional, List
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
from config.settings import LLM_TEMPERATURE, AGENT_PROMPTS, TASK_TEMPLATES, MESSAGES
from modules.mcp_tools import MCPToolManager


class AIAgentError(Exception):
    """Exceção customizada para erros nos agentes de IA"""
    pass


class AIAgentManager:
    """
    Gerenciador de agentes de IA focado em Ollama
    """
    
    def __init__(self, ollama_model: str = "llama3.1:8b"):
        """
        Inicializa o gerenciador de agentes com Ollama Local
        """
        try:
            base_url = "http://localhost:11434"
            
            # Verificação de saúde do servidor Ollama
            try:
                health_check = requests.get(f"{base_url}/api/tags", timeout=2)
                if health_check.status_code != 200:
                    raise AIAgentError("O servidor Ollama respondeu com erro.")
            except Exception:
                raise AIAgentError("❌ Ollama não está respondendo localmente. Verifique se o app Ollama está aberto.")

            st.info(f"🤖 Conectado ao Ollama Local (Modelo: {ollama_model})")
            
            # Inicializar o modelo Ollama como motor principal
            self.llm = Ollama(
                model=ollama_model,
                base_url=base_url,
                temperature=LLM_TEMPERATURE
            )
            
            # Inicializar ferramentas MCP
            self.tool_manager = MCPToolManager()
            self.tools = self.tool_manager.get_all_tools()
            
        except Exception as e:
            raise AIAgentError(f"Erro ao inicializar Ollama: {e}")
    
    def create_data_analyst_agent(self) -> Agent:
        """Cria o agente de análise de dados"""
        config = AGENT_PROMPTS["data_analyst"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm,
            tools=[self.tools[0]], 
            allow_delegation=False,
            verbose=True
        )
    
    def create_sdr_agent(self) -> Agent:
        """Cria o agente SDR"""
        config = AGENT_PROMPTS["sdr"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm,
            tools=[self.tools[1], self.tools[2]], 
            allow_delegation=False,
            verbose=True
        )
    
    def create_analysis_task(self, agent: Agent, batch_text: str) -> Task:
        """Cria a tarefa de análise"""
        template = TASK_TEMPLATES["analysis"]
        description = template["description"].format(batch_text=batch_text)
        return Task(
            description=description,
            expected_output=template["expected_output"],
            agent=agent
        )
    
    def create_cadence_task(self, agent: Agent) -> Task:
        """Cria a tarefa de cadência"""
        template = TASK_TEMPLATES["cadence"]
        return Task(
            description=template["description"],
            expected_output=template["expected_output"],
            agent=agent
        )
    
    def execute_crew(self, agents: list, tasks: list) -> Optional[str]:
        """Executa a crew"""
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
            st.error(f"Erro na execução da crew: {e}")
            raise AIAgentError(f"Erro na execução da crew: {e}")
    
    def process_batch(self, batch_text: str) -> Optional[str]:
        """Processa lote de leads"""
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
            st.error(f"Erro no processamento: {e}")
            raise AIAgentError(f"Erro no processamento: {e}")


def validate_and_initialize_ai(ollama_model: str = "llama3.1:8b") -> Optional[AIAgentManager]:
    """Inicializa o gerenciador de IA focado em Ollama"""
    try:
        return AIAgentManager(ollama_model=ollama_model)
    except AIAgentError as e:
        st.error(str(e))
        return None
