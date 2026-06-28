import os
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import ScrapeWebsiteTool
from config.settings import DEFAULT_LLM_MODEL, LLM_TEMPERATURE, AGENT_PROMPTS, TASK_TEMPLATES

class AIAgentManager:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        os.environ["GOOGLE_API_KEY"] = self.api_key
        # Armazenamos a configuração, mas não o objeto LLM instanciado agora
        self.llm_config = {
            "model": DEFAULT_LLM_MODEL,
            "temperature": LLM_TEMPERATURE,
            "google_api_key": self.api_key
        }

    def _get_llm(self):
        return ChatGoogleGenerativeAI(**self.llm_config)
    
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

    # (Métodos restantes permanecem iguais aos anteriores)
    def create_analysis_task(self, agent, batch_text):
        template = TASK_TEMPLATES["analysis"]
        return Task(description=template["description"].format(batch_text=batch_text), expected_output=template["expected_output"], agent=agent)
    
    def create_cadence_task(self, agent):
        template = TASK_TEMPLATES["cadence"]
        return Task(description=template["description"], expected_output=template["expected_output"], agent=agent)
    
    def execute_crew(self, agents, tasks):
        crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
        return str(crew.kickoff())

    def process_batch(self, batch_text):
        data_analyst = self.create_data_analyst_agent()
        sdr_agent = self.create_sdr_agent()
        analysis_task = self.create_analysis_task(data_analyst, batch_text)
        cadence_task = self.create_cadence_task(sdr_agent)
        return self.execute_crew(agents=[data_analyst, sdr_agent], tasks=[analysis_task, cadence_task])
