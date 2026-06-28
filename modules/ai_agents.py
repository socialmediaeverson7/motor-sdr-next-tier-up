import os
import streamlit as st
from typing import List, Optional
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import ScrapeWebsiteTool
from config.settings import DEFAULT_LLM_MODEL, LLM_TEMPERATURE, AGENT_PROMPTS, TASK_TEMPLATES, MESSAGES

class AIAgentError(Exception):
    pass

class AIAgentManager:
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise AIAgentError("Chave de API não fornecida")
        self.api_key = api_key.strip()
        os.environ["GOOGLE_API_KEY"] = self.api_key

    # Criamos o objeto LLM internamente apenas quando necessário
    def _get_llm(self):
        return ChatGoogleGenerativeAI(
            model=DEFAULT_LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            google_api_key=self.api_key
        )
    
    def create_data_analyst_agent(self) -> Agent:
        config = AGENT_PROMPTS["data_analyst"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self._get_llm(),
            tools=[ScrapeWebsiteTool()],
            allow_delegation=False,
            verbose=True
        )
    
    def create_sdr_agent(self) -> Agent:
        config = AGENT_PROMPTS["sdr"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self._get_llm(),
            allow_delegation=False,
            verbose=True
        )

    # (Métodos de Task e Crew permanecem os mesmos)
    def create_analysis_task(self, agent: Agent, batch_text: str) -> Task:
        template = TASK_TEMPLATES["analysis"]
        return Task(description=template["description"].format(batch_text=batch_text), 
                    expected_output=template["expected_output"], agent=agent)
    
    def create_cadence_task(self, agent: Agent) -> Task:
        template = TASK_TEMPLATES["cadence"]
        return Task(description=template["description"], 
                    expected_output=template["expected_output"], agent=agent)
    
    def execute_crew(self, agents: List[Agent], tasks: List[Task]) -> str:
        crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
        return str(crew.kickoff())
    
    def process_batch(self, batch_text: str) -> str:
        data_analyst = self.create_data_analyst_agent()
        sdr_agent = self.create_sdr_agent()
        analysis_task = self.create_analysis_task(data_analyst, batch_text)
        cadence_task = self.create_cadence_task(sdr_agent)
        return self.execute_crew(agents=[data_analyst, sdr_agent], tasks=[analysis_task, cadence_task])

def validate_and_initialize_ai(api_key: str) -> Optional[AIAgentManager]:
    try:
        return AIAgentManager(api_key)
    except Exception as e:
        st.error(f"Erro na inicialização: {e}")
        return None
