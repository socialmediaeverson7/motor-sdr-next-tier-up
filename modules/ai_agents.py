"""
Módulo de Agentes de IA
Implementa os agentes CrewAI para análise e geração de cadências
"""

import os
import streamlit as st
from typing import Tuple, Optional
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
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
        """
        Inicializa o gerenciador de agentes
        
        Args:
            api_key: Chave de API do Google Gemini
        
        Raises:
            AIAgentError: Se a chave de API for inválida
        """
        if not api_key or not api_key.strip():
            raise AIAgentError("Chave de API do Gemini não fornecida")
        
        try:
            # Limpar espaços em branco extras que podem causar erro 400
            clean_api_key = api_key.strip()
            
            # Configurar variável de ambiente para garantir compatibilidade com bibliotecas que a utilizam
            os.environ["GOOGLE_API_KEY"] = clean_api_key
            
            # Inicializar o modelo passando a chave explicitamente para evitar dependência apenas de env vars
            self.llm = ChatGoogleGenerativeAI(
                model=DEFAULT_LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                google_api_key=clean_api_key  # Passagem explícita da chave
            )
        except Exception as e:
            raise AIAgentError(f"Erro ao inicializar modelo de IA: {e}")
    
    def create_data_analyst_agent(self) -> Agent:
        """
        Cria o agente de análise de dados
        
        Returns:
            Agent: Agente configurado para análise de dados
        """
        config = AGENT_PROMPTS["data_analyst"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )
    
    def create_sdr_agent(self) -> Agent:
        """
        Cria o agente SDR de alta escala
        
        Returns:
            Agent: Agente configurado para geração de cadências
        """
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
        """
        Cria a tarefa de análise de lote
        
        Args:
            agent: Agente que executará a tarefa
            batch_text: Texto formatado com os leads
        
        Returns:
            Task: Tarefa configurada para análise
        """
        template = TASK_TEMPLATES["analysis"]
        description = template["description"].format(batch_text=batch_text)
        
        return Task(
            description=description,
            expected_output=template["expected_output"],
            agent=agent
        )
    
    def create_cadence_task(self, agent: Agent) -> Task:
        """
        Cria a tarefa de geração de cadências
        
        Args:
            agent: Agente que executará a tarefa
        
        Returns:
            Task: Tarefa configurada para geração de cadências
        """
        template = TASK_TEMPLATES["cadence"]
        
        return Task(
            description=template["description"],
            expected_output=template["expected_output"],
            agent=agent
        )
    
    def execute_crew(self, agents: list, tasks: list) -> Optional[str]:
        """
        Executa uma crew com os agentes e tarefas fornecidos
        
        Args:
            agents: Lista de agentes
            tasks: Lista de tarefas
        
        Returns:
            str: Resultado da execução da crew
        
        Raises:
            AIAgentError: Se houver erro na execução
        """
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
            error_msg = MESSAGES["error_llm_processing"].format(error=str(e))
            st.error(error_msg)
            raise AIAgentError(f"Erro na execução da crew: {e}")
    
    def process_batch(self, batch_text: str) -> Optional[str]:
        """
        Processa um lote de leads através dos agentes de análise e SDR
        
        Args:
            batch_text: Texto formatado com os leads
        
        Returns:
            str: Resultado do processamento em lote
        
        Raises:
            AIAgentError: Se houver erro no processamento
        """
        try:
            # Criar agentes
            data_analyst = self.create_data_analyst_agent()
            sdr_agent = self.create_sdr_agent()
            
            # Criar tarefas
            analysis_task = self.create_analysis_task(data_analyst, batch_text)
            cadence_task = self.create_cadence_task(sdr_agent)
            
            # Executar crew
            result = self.execute_crew(
                agents=[data_analyst, sdr_agent],
                tasks=[analysis_task, cadence_task]
            )
            
            return result
            
        except AIAgentError:
            raise
        except Exception as e:
            error_msg = MESSAGES["error_llm"].format(error=str(e))
            st.error(error_msg)
            raise AIAgentError(f"Erro crítico no motor de IA: {e}")


def validate_and_initialize_ai(api_key: str) -> Optional[AIAgentManager]:
    """
    Valida e inicializa o gerenciador de agentes de IA
    
    Args:
        api_key: Chave de API do Google Gemini
    
    Returns:
        AIAgentManager: Gerenciador inicializado ou None se houver erro
    """
    try:
        if not api_key or not api_key.strip():
            st.error(MESSAGES["error_api_key"])
            return None
        
        # Teste rápido de conectividade (opcional, mas útil para feedback imediato)
        # manager = AIAgentManager(api_key)
        # return manager
        
        return AIAgentManager(api_key)
        
    except AIAgentError as e:
        st.error(f"Erro na inicialização da IA: {e}")
        return None
