"""
Módulo de Bots de Extração de Leads
Implementa diferentes estratégias para extrair dados de empresas-alvo com resiliência
"""

import requests
import streamlit as st
import time
from datetime import datetime
from typing import List, Dict
from config.settings import API_TIMEOUT, MAX_LEADS_PER_REQUEST, MESSAGES, API_RETRY_ATTEMPTS


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
        Extrai leads de licitações recentes do PNCP com Retry Exponencial
        """
        for attempt in range(API_RETRY_ATTEMPTS):
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
                if attempt < API_RETRY_ATTEMPTS - 1:
                    wait_time = (attempt + 1) * 5
                    st.warning(f"⚠️ Tentativa {attempt + 1} falhou no PNCP. Tentando novamente em {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    error_msg = MESSAGES["error_pncp_bot"].format(error=str(e))
                    st.error(error_msg)
                    raise LeadExtractionError(f"PNCP Bot Error: {e}")
            except Exception as e:
                raise LeadExtractionError(f"Erro inesperado no PNCP: {e}")


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
            
        except Exception as e:
            st.error(f"Erro no Sniper Bot: {e}")
            raise LeadExtractionError(f"Sniper Nicho Bot Error: {e}")


class OSINTReceitaBot:
    """
    Bot para extração de dados de empresas via CNPJ
    """
    
    BASE_URL = "https://receitaws.com.br/v1/cnpj"
    
    @staticmethod
    def extract(cnpj: str) -> List[Dict[str, str]]:
        """
        Extrai informações detalhadas de uma empresa via CNPJ
        """
        try:
            from modules.utils import clean_cnpj
            cnpj_limpo = clean_cnpj(cnpj)
            
            response = requests.get(
                f"{OSINTReceitaBot.BASE_URL}/{cnpj_limpo}",
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "ERROR":
                raise LeadExtractionError("CNPJ não encontrado")
            
            lead = {
                "alvo": data.get('nome', 'N/A'),
                "contexto": f"Atividade: {data.get('atividade_principal', [{}])[0].get('text', 'N/A')}"
            }
            
            return [lead]
            
        except Exception as e:
            st.error(f"Erro no OSINT Bot: {e}")
            raise LeadExtractionError(f"OSINT Receita Bot Error: {e}")


def get_leads_by_strategy(strategy: str, search_term: str = "", cnpj: str = "") -> List[Dict[str, str]]:
    """
    Função auxiliar com lógica de Fallback Automático
    """
    try:
        if strategy == "pncp":
            try:
                return PNCPBot.extract()
            except LeadExtractionError:
                st.info("🔄 PNCP instável. Ativando Fallback: Buscando empresas de Tecnologia via Sniper...")
                return SniperNichoBot.extract("Empresas de Tecnologia")
        elif strategy == "sniper":
            return SniperNichoBot.extract(search_term)
        elif strategy == "cnpj":
            return OSINTReceitaBot.extract(cnpj)
        else:
            raise LeadExtractionError(f"Estratégia desconhecida: {strategy}")
    except Exception as e:
        raise LeadExtractionError(str(e))
