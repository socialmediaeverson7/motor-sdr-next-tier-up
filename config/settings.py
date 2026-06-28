"""
Configurações e constantes da aplicação Motor SDR
"""

# ============================================================================
# CONFIGURAÇÕES DE SEGURANÇA E TELEMETRIA
# ============================================================================

import os

# Desabilitar telemetria e tracing
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = "disabled"

# ============================================================================
# CONFIGURAÇÕES DE STREAMLIT
# ============================================================================

STREAMLIT_CONFIG = {
    "page_title": "Motor SDR - Next Tier Up",
    "page_icon": "🎯",
    "layout": "wide",
}

# ============================================================================
# CONFIGURAÇÕES DE TIMEOUTS E LIMITES
# ============================================================================

API_TIMEOUT = 15  # segundos
API_RETRY_ATTEMPTS = 3
MAX_LEADS_PER_REQUEST = 1

# ============================================================================
# CONFIGURAÇÕES DE MODELOS DE IA
# ============================================================================

DEFAULT_LLM_MODEL = "gemini-1.5-pro"
LLM_TEMPERATURE = 0.7

# ============================================================================
# CONFIGURAÇÕES DE E-MAIL
# ============================================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ============================================================================
# MENSAGENS DE ERRO E SUCESSO
# ============================================================================

MESSAGES = {
    "error_api_key": "⚠️ Insira a chave do Gemini.",
    "error_email_credentials": "Preencha seu E-mail e Senha de App na barra lateral!",
    "error_email_destination": "Preencha o e-mail de destino.",
    "error_pncp_bot": "⚠️ Erro no Bot do PNCP: {error}",
    "error_sniper_bot": "⚠️ Erro no mapa: {error}",
    "error_cnpj_bot": "⚠️ Erro CNPJ: {error}",
    "error_llm": "Erro crítico no motor de IA: {error}",
    "error_llm_processing": "Erro na IA: {error}",
    "error_smtp": "Erro no servidor SMTP: {error}",
    "success_email": "Vitória! E-mail disparado para {email} 🎯",
    "warning_no_leads": "Nenhum alvo encontrado.",
    "info_batch_ready": "🔥 Lote de {count} alvos montado. Injetando no Cérebro da IA...",
}

# ============================================================================
# PROMPTS E TEMPLATES
# ============================================================================

AGENT_PROMPTS = {
    "data_analyst": {
        "role": "Analista de Inteligência Operacional",
        "goal": "Analisar um lote de empresas de uma só vez, identificando oportunidades e dores comerciais.",
        "backstory": "Você é um especialista em análise de dados comerciais que processa listas brutas de prospecção e extrai insights valiosos.",
    },
    "sdr": {
        "role": "SDR de Alta Escala",
        "goal": "Gerar cadências omnichannel rápidas e personalizadas para uma lista de empresas.",
        "backstory": "Você é um especialista em vendas que cria abordagens curtas e agressivas focadas em conversão. Para cada empresa da lista, gere os blocos: [E-MAIL], [LINKEDIN] e [CALL].",
    },
}

TASK_TEMPLATES = {
    "analysis": {
        "description": "Leia a seguinte lista de empresas extraídas da web:\n{batch_text}\n\nPara cada empresa, realize uma análise detalhada incluindo:\n1. Dor comercial principal\n2. Oportunidades de alavancagem\n3. Possível decisor ou departamento-alvo",
        "expected_output": "Análise estruturada em lote com insights por empresa.",
    },
    "cadence": {
        "description": "Com base na análise do lote, crie uma cadência personalizada para CADA empresa da lista. Para cada empresa, formate a resposta com os seguintes blocos:\n\n[EMPRESA]\n[E-MAIL] - Assunto e corpo otimizado\n[LINKEDIN] - Mensagem de conexão\n[CALL] - Script de abertura\n\nGaranta que cada cadência seja específica e pronta para ação.",
        "expected_output": "Relatório Mestre de Prospecção com cadências estruturadas e prontas para execução.",
    },
}
