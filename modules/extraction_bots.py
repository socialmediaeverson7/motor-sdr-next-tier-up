"""
Módulo de Bots de Extração de Leads
Implementa diferentes estratégias para extrair dados de empresas-alvo
"""

import requests
import streamlit as st
from datetime import datetime
from typing import List, Dict
from config.settings import API_TIMEOUT, MAX_LEADS_PER_REQUEST, MESSAGES


class LeadExtractionError(Exception):
    """Exceção customizada para erros na extração de leads"""
    pass


class PNCPBot:
    """
    Bot para extração de leads do Portal Nacional de Contratações Públicas (PNCP)
    Identifica empresas que ganharam licitações recentemente
    """
    
    BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratos"
    
    @staticmethod
    def extract() -> List[Dict[str, str]]:
        """
        Extrai leads de licitações recentes do PNCP
        
        Returns:
            List[Dict]: Lista de leads com 'alvo' e 'contexto'
        
        Raises:
            LeadExtractionError: Se houver erro na requisição
        """
        try:
            hoje = datetime.now().strftime("%Y%m%d")
            params = {
                "dataInicial": hoje,
                "dataFinal": hoje,
                "pagina": 1
            }
            
            response = requests.get(
                PNCPBot.BASE_URL,
                params=params,
                headers={'accept': 'application/json'},
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            leads = []
            data = response.json().get('data', [])
            
            for contract in data[:MAX_LEADS_PER_REQUEST]:
                if contract.get('niFornecedor'):
                    leads.append({
                        "alvo": contract.get('nomeRazaoSocialFornecedor', 'N/A'),
                        "contexto": f"Ganhou licitação para: {contract.get('objetoContrato', 'Serviços/Obras')}"
                    })
            
            return leads
            
        except requests.exceptions.RequestException as e:
            error_msg = MESSAGES["error_pncp_bot"].format(error=str(e))
            st.error(error_msg)
            raise LeadExtractionError(f"PNCP Bot Error: {e}")
        except Exception as e:
            error_msg = MESSAGES["error_pncp_bot"].format(error=str(e))
            st.error(error_msg)
            raise LeadExtractionError(f"PNCP Bot Error: {e}")


class SniperNichoBot:
    """
    Bot para extração de leads por nicho e região
    Utiliza a API Nominatim do OpenStreetMap para buscar empresas
    """
    
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    
    @staticmethod
    def extract(search_term: str) -> List[Dict[str, str]]:
        """
        Extrai leads de um nicho e região específicos
        
        Args:
            search_term: Termo de busca (ex: "Transportadora em Uberlândia")
        
        Returns:
            List[Dict]: Lista de leads com 'alvo' e 'contexto'
        
        Raises:
            LeadExtractionError: Se houver erro na requisição
        """
        try:
            params = {
                "q": search_term,
                "format": "json",
                "limit": MAX_LEADS_PER_REQUEST,
                "addressdetails": 1
            }
            headers = {"User-Agent": "MotorSDR_NextTierUp_Bot/4.0"}
            
            response = requests.get(
                SniperNichoBot.BASE_URL,
                params=params,
                headers=headers,
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            leads = []
            results = response.json()
            
            for result in results:
                display_name = result.get('display_name', '')
                company_name = display_name.split(',')[0] if display_name else 'N/A'
                
                leads.append({
                    "alvo": company_name,
                    "contexto": f"Localização: {display_name}"
                })
            
            return leads
            
        except requests.exceptions.RequestException as e:
            error_msg = MESSAGES["error_sniper_bot"].format(error=str(e))
            st.error(error_msg)
            raise LeadExtractionError(f"Sniper Nicho Bot Error: {e}")
        except Exception as e:
            error_msg = MESSAGES["error_sniper_bot"].format(error=str(e))
            st.error(error_msg)
            raise LeadExtractionError(f"Sniper Nicho Bot Error: {e}")


class OSINTReceitaBot:
    """
    Bot para extração de dados de empresas via CNPJ
    Utiliza a API ReceitaWS para obter informações detalhadas
    """
    
    BASE_URL = "https://receitaws.com.br/v1/cnpj"
    
    @staticmethod
    def extract(cnpj: str) -> List[Dict[str, str]]:
        """
        Extrai informações detalhadas de uma empresa via CNPJ
        
        Args:
            cnpj: CNPJ da empresa (com ou sem formatação)
        
        Returns:
            List[Dict]: Lista com um lead contendo dados da empresa
        
        Raises:
            LeadExtractionError: Se houver erro na requisição ou CNPJ inválido
        """
        try:
            from modules.utils import clean_cnpj
            
            cnpj_limpo = clean_cnpj(cnpj)
            
            if len(cnpj_limpo) != 14:
                raise LeadExtractionError("CNPJ deve conter 14 dígitos")
            
            response = requests.get(
                f"{OSINTReceitaBot.BASE_URL}/{cnpj_limpo}",
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "ERROR":
                raise LeadExtractionError("CNPJ não encontrado ou inválido")
            
            # Extrair informações dos sócios
            partners = [s.get('nome') for s in data.get('qsa', [])]
            partners_str = ', '.join(partners) if partners else "Não disponível"
            
            lead = {
                "alvo": data.get('nome', 'N/A'),
                "contexto": f"Capital Social: R$ {data.get('capital_social', 'N/A')} | Sócios: {partners_str}"
            }
            
            return [lead]
            
        except requests.exceptions.RequestException as e:
            error_msg = MESSAGES["error_cnpj_bot"].format(error=str(e))
            st.error(error_msg)
            raise LeadExtractionError(f"OSINT Receita Bot Error: {e}")
        except LeadExtractionError as e:
            error_msg = MESSAGES["error_cnpj_bot"].format(error=str(e))
            st.error(error_msg)
            raise
        except Exception as e:
            error_msg = MESSAGES["error_cnpj_bot"].format(error=str(e))
            st.error(error_msg)
            raise LeadExtractionError(f"OSINT Receita Bot Error: {e}")


def get_leads_by_strategy(strategy: str, search_term: str = "", cnpj: str = "") -> List[Dict[str, str]]:
    """
    Função auxiliar para extrair leads baseada na estratégia selecionada
    
    Args:
        strategy: Estratégia de extração ("pncp", "sniper", "cnpj")
        search_term: Termo de busca (para estratégia "sniper")
        cnpj: CNPJ da empresa (para estratégia "cnpj")
    
    Returns:
        List[Dict]: Lista de leads extraídos
    """
    try:
        if strategy == "pncp":
            return PNCPBot.extract()
        elif strategy == "sniper":
            return SniperNichoBot.extract(search_term)
        elif strategy == "cnpj":
            return OSINTReceitaBot.extract(cnpj)
        else:
            raise LeadExtractionError(f"Estratégia desconhecida: {strategy}")
    except LeadExtractionError:
        raise
