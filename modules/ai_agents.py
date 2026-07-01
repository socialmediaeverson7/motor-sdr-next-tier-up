"""
Módulo de Agentes de IA
Implementa os agentes CrewAI para análise e geração de cadências com suporte a Gemini e Ollama
"""

import os
import streamlit as st
from typing import Tuple, Optional, List
import requests
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from config.settings import DEFAULT_LLM_MODEL, LLM_TEMPERATURE, AGENT_PROMPTS, TASK_TEMPLATES, MESSAGES
from modules.mcp_tools import MCPToolManager


class AIAgentError(Exception):
    """Exceção customizada para erros nos agentes de IA"""
    pass


class AIAgentManager:
    """
    Gerenciador de agentes de IA
    Responsável por criar, configurar e executar agentes CrewAI
    """
    
    def __init__(self, api_key: str = None, provider: str = "Google Gemini", ollama_model: str = "qwen2.5-coder:7b"):
        """
        Inicializa o gerenciador de agentes com suporte a múltiplos provedores
        Com fallback automático de Ollama para Gemini
        """
        self.provider_used = provider
        
        try:
            if provider == "Ollama Local":
                # Verificar se Ollama está disponível
                if self._check_ollama_availability():
                    st.info(f"🤖 Conectando ao Ollama Local (Modelo: {ollama_model})...")
                    self.llm = Ollama(
                        model=ollama_model,
                        base_url="http://127.0.0.1:11434",
                        request_timeout=60.0
                    )
                    self.provider_used = "Ollama Local"
                else:
                    # Fallback para Gemini se Ollama não está disponível
                    st.warning("⚠️ Ollama não disponível. Usando Google Gemini como fallback...")
                    self._initialize_gemini(api_key)
                    self.provider_used = "Google Gemini (Fallback)"
            else:
                self._initialize_gemini(api_key)
                self.provider_used = "Google Gemini"
            
            # Inicializar ferramentas MCP
            self.tool_manager = MCPToolManager()
            self.tools = self.tool_manager.get_all_tools()
            
            st.success(f"✅ IA inicializada com: {self.provider_used}")
            
        except Exception as e:
            raise AIAgentError(f"Erro ao inicializar modelo de IA: {e}")
    
    def _check_ollama_availability(self) -> bool:
        """
        Verifica se o Ollama está rodando e disponível
        """
        try:
            response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False
        except Exception:
            return False
    
    def _initialize_gemini(self, api_key: str) -> None:
        """
        Inicializa o modelo Gemini
        """
        if not api_key or not api_key.strip():
            raise AIAgentError("Chave de API do Gemini não fornecida e Ollama não disponível")
        
        # Limpar espaços em branco extras
        clean_api_key = api_key.strip()
        os.environ["GOOGLE_API_KEY"] = clean_api_key
        
        # Inicializar o modelo Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=DEFAULT_LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            google_api_key=clean_api_key
        )
    
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


def validate_and_initialize_ai(api_key: str = None, provider: str = "Google Gemini", ollama_model: str = "qwen2.5-coder:7b") -> Optional[AIAgentManager]:
    """
    Valida e inicializa o gerenciador de agentes de IA
    Com fallback automático para Gemini se Ollama não estiver disponível
    """
    try:
        return AIAgentManager(api_key=api_key, provider=provider, ollama_model=ollama_model)
    except AIAgentError as e:
        st.error(f"Erro na inicialização da IA: {e}")
        return None
