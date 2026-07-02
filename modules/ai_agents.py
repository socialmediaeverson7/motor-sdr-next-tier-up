"""
Módulo de Agentes de IA
Implementa os agentes CrewAI para análise e geração de cadências com Ollama Local
"""

import os
import streamlit as st
from typing import Optional, List
import requests
from urllib3.exceptions import InsecureRequestWarning
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
from config.settings import DEFAULT_LLM_MODEL, LLM_TEMPERATURE, AGENT_PROMPTS, TASK_TEMPLATES, MESSAGES
from modules.mcp_tools import MCPToolManager

# Desabilitar aviso de SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class AIAgentError(Exception):
    """Exceção customizada para erros nos agentes de IA"""
    pass


class AIAgentManager:
    """
    Gerenciador de agentes de IA
    Responsável por criar, configurar e executar agentes CrewAI com Ollama Local
    """
    
    # ALTERADO: Modelo padrão focado em SDR e estruturação de dados (Llama 3.1)
    def __init__(self, ollama_model: str = "llama3.1:8b"):
        """
        Inicializa o gerenciador de agentes com Ollama Local
        """
        try:
            # Verificar se Ollama está disponível
            if not self._check_ollama_availability():
                raise AIAgentError(
                    "❌ Ollama não está respondendo localmente.\n\n"
                    "Por favor, verifique se o ícone da Lhama está na barra de tarefas."
                )
            
            st.info(f"🤖 Conectando ao Ollama Local (Modelo: {ollama_model})...")
            
            # Inicializar Ollama
            self.llm = Ollama(
                model=ollama_model,
                base_url="http://127.0.0.1:11434",
                request_timeout=120.0
            )
            
            # Inicializar ferramentas MCP
            self.tool_manager = MCPToolManager()
            self.tools = self.tool_manager.get_all_tools()
            
            st.success(f"✅ IA inicializada com sucesso usando Ollama Local ({ollama_model})")
            
        except AIAgentError:
            raise
        except Exception as e:
            raise AIAgentError(f"Erro ao inicializar Ollama: {e}")
    
    def _check_ollama_availability(self) -> bool:
        """
        Verifica se o Ollama está rodando batendo na porta principal,
        exatamente como testado via terminal.
        """
        # Usando a URL raiz que provamos estar funcionando
        url = "http://127.0.0.1:11434"
        
        session = requests.Session()
        session.trust_env = False 
        
        try:
            # Faz a mesma requisição do seu teste de terminal
            response = session.get(url, timeout=5, verify=False)
            if response.status_code == 200 and "Ollama is running" in response.text:
                st.info("✅ Ollama detectado e conectado na porta raiz!")
                return True
        except Exception:
            pass
            
        return False
    
    def create_data_analyst_agent(self) -> Agent:
        """
        Cria o agente de análise de dados com ferramentas de pesquisa
        """
        config = AGENT_PROMPTS["data_analyst"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm,
            tools=[self.tools[0]], # Ferramenta de pesquisa
            allow_delegation=False,
            verbose=True
        )
    
    def create_sdr_agent(self) -> Agent:
        """
        Cria o agente SDR de alta escala com ferramentas de produtividade
        """
        config = AGENT_PROMPTS["sdr"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm,
            tools=[self.tools[1], self.tools[2]], # CRM e Sheets
            allow_delegation=False,
            verbose=True
        )
    
    def create_analysis_task(self, agent: Agent, batch_text: str) -> Task:
        """
        Cria a tarefa de análise de lote
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


def validate_and_initialize_ai(ollama_model: str = "llama3.1:8b") -> Optional[AIAgentManager]:
    """
    Valida e inicializa o gerenciador de agentes de IA com Ollama Local
    """
    try:
        return AIAgentManager(ollama_model=ollama_model)
    except AIAgentError as e:
        st.error(f"Erro na inicialização da IA: {e}")
        return None
