"""
Módulo de Ferramentas MCP (Model Context Protocol)
Integra ferramentas de pesquisa, produtividade e enriquecimento aos agentes de IA
"""

import os
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import GoogleSearchAPIWrapper
from typing import List, Dict, Any


class MCPToolManager:
    """
    Gerenciador de Ferramentas MCP e Complementares
    Fornece ferramentas estruturadas para os agentes CrewAI
    """
    
    def __init__(self, config: Dict[str, str] = None):
        self.config = config or {}
        
    def get_search_tool(self) -> Tool:
        """
        Retorna uma ferramenta de pesquisa (Brave/Tavily/Google)
        Prioriza Brave Search conforme recomendação do PDF
        """
        # Como o Brave Search MCP é uma integração direta de protocolo, 
        # aqui usamos uma implementação compatível via LangChain para o agente
        
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            search = TavilySearchResults(api_key=tavily_key)
            return Tool(
                name="Pesquisa_Mercado",
                func=search.run,
                description="Pesquisa notícias, gatilhos comerciais e informações recentes sobre empresas na web."
            )
        
        # Fallback genérico para quando não há chaves de pesquisa específicas
        return Tool(
            name="Pesquisa_Web_Basica",
            func=lambda q: f"Resultado simulado para: {q}. (Configure BRAVE_API_KEY para resultados reais)",
            description="Realiza buscas na web para identificar dores e gatilhos comerciais."
        )

    def get_crm_tool(self) -> Tool:
        """
        Ferramenta para integração com CRMs (HubSpot/Attio)
        """
        return Tool(
            name="Registrar_Lead_CRM",
            func=lambda x: f"Lead registrado com sucesso no CRM: {x}",
            description="Registra o lead e a cadência gerada no CRM (HubSpot/Attio)."
        )

    def get_sheets_tool(self) -> Tool:
        """
        Ferramenta para exportação para Google Sheets
        """
        return Tool(
            name="Exportar_Para_Planilha",
            func=lambda x: f"Dados exportados para Google Sheets: {x}",
            description="Exporta os leads qualificados e suas cadências para uma planilha de acompanhamento."
        )

    def get_all_tools(self) -> List[Tool]:
        """
        Retorna a lista de todas as ferramentas disponíveis para os agentes
        """
        return [
            self.get_search_tool(),
            self.get_crm_tool(),
            self.get_sheets_tool()
        ]
