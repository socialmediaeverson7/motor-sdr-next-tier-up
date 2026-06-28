"""
Funções utilitárias para o Motor SDR
"""

import re
from typing import Optional


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida um CNPJ brasileiro.
    
    Args:
        cnpj: String contendo o CNPJ (com ou sem formatação)
    
    Returns:
        bool: True se o CNPJ é válido, False caso contrário
    """
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj_limpo) != 14:
        return False
    
    # Verificação de dígitos verificadores (simplificada)
    if cnpj_limpo == cnpj_limpo[0] * 14:
        return False
    
    return True


def validate_email(email: str) -> bool:
    """
    Valida um endereço de e-mail.
    
    Args:
        email: String contendo o endereço de e-mail
    
    Returns:
        bool: True se o e-mail é válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_api_key(api_key: str) -> bool:
    """
    Valida se uma chave de API foi fornecida (validação básica).
    
    Args:
        api_key: String contendo a chave de API
    
    Returns:
        bool: True se a chave não está vazia, False caso contrário
    """
    return bool(api_key and api_key.strip())


def clean_cnpj(cnpj: str) -> str:
    """
    Remove caracteres não numéricos de um CNPJ.
    
    Args:
        cnpj: String contendo o CNPJ
    
    Returns:
        str: CNPJ contendo apenas dígitos
    """
    return ''.join(filter(str.isdigit, cnpj))


def format_leads_for_batch(leads: list) -> str:
    """
    Formata uma lista de leads para o processamento em lote.
    
    Args:
        leads: Lista de dicionários com chaves 'alvo' e 'contexto'
    
    Returns:
        str: String formatada para envio aos agentes de IA
    """
    if not leads:
        return ""
    
    formatted = []
    for idx, lead in enumerate(leads, 1):
        formatted.append(f"{idx}. Empresa: {lead.get('alvo', 'N/A')} | Dados: {lead.get('contexto', 'N/A')}")
    
    return "\n".join(formatted)


def extract_json_from_text(text: str) -> Optional[dict]:
    """
    Tenta extrair um bloco JSON de um texto.
    
    Args:
        text: String contendo potencialmente um bloco JSON
    
    Returns:
        dict: Dicionário extraído ou None se não encontrado
    """
    import json
    
    # Procura por padrão de JSON
    json_pattern = r'\{[\s\S]*\}'
    match = re.search(json_pattern, text)
    
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    
    return None


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Trunca um texto para um comprimento máximo.
    
    Args:
        text: String a ser truncada
        max_length: Comprimento máximo desejado
    
    Returns:
        str: Texto truncado com "..." se necessário
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."
