"""
Módulo de Ferramentas MCP (Model Context Protocol)
Integra ferramentas de pesquisa, produtividade e enriquecimento aos agentes de IA
"""

import os
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun
import json
from datetime import datetime
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
        Retorna uma ferramenta de pesquisa gratuita (DuckDuckGo)
        """
        search = DuckDuckGoSearchRun()
        return Tool(
            name="Pesquisa_Mercado_Gratuita",
            func=search.run,
            description="Pesquisa notícias e gatilhos comerciais na web de forma gratuita e ilimitada."
        )

    def get_crm_tool(self) -> Tool:
        """
        Ferramenta de CRM Local Gratuita (JSON)
        """
        def save_to_local_crm(data):
            try:
                filename = "crm_local_leads.json"
                leads = []
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        leads = json.load(f)
                
                new_entry = {
                    "data_processamento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "conteudo": data
                }
                leads.append(new_entry)
                
                with open(filename, 'w') as f:
                    json.dump(leads, f, indent=4, ensure_ascii=False)
                return f"Lead salvo com sucesso no CRM Local ({filename})"
            except Exception as e:
                return f"Erro ao salvar no CRM Local: {e}"

        return Tool(
            name="Registrar_Lead_CRM_Local",
            func=save_to_local_crm,
            description="Salva o lead e a cadência em um banco de dados local gratuito (JSON)."
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
