"""
Módulo de Interface do Usuário (Streamlit)
Implementa todos os componentes da UI da aplicação
"""

import streamlit as st
import urllib.parse
from typing import Tuple
from config.settings import STREAMLIT_CONFIG, MESSAGES


def configure_page():
    """
    Configura as definições da página Streamlit
    """
    st.set_page_config(**STREAMLIT_CONFIG)


def render_sidebar() -> Tuple[str, str, str, str, str, str]:
    """
    Renderiza a barra lateral com inputs do usuário
    
    Returns:
        Tuple: (api_key, sender_email, sender_password, strategy, search_term/cnpj)
    """
    # Tentar carregar chaves automáticas
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Prioridade: 1. st.secrets, 2. os.environ (.env), 3. Vazio
    default_api_key = ""
    try:
        default_api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    except:
        default_api_key = os.getenv("GOOGLE_API_KEY", "")

    default_email = os.getenv("SENDER_EMAIL", "")
    default_password = os.getenv("SENDER_PASSWORD", "")

    with st.sidebar:
        st.header("⚙️ Configuração de IA")
        ai_provider = st.selectbox(
            "Provedor de IA:",
            ["Google Gemini", "Ollama Local"],
            index=0,
            help="Escolha entre usar a nuvem (Gemini) ou sua máquina local (Ollama)."
        )
        
        api_key = None
        ollama_model = "llama3"
        
        if ai_provider == "Google Gemini":
            api_key = st.text_input(
                "Chave do Gemini:", 
                value=default_api_key, 
                type="password", 
                help="Carregada automaticamente de .env ou st.secrets se disponível."
            )
        else:
            ollama_model = st.selectbox(
                "Selecione o Modelo Ollama:",
                ["llama3.1:8b", "qwen2.5-coder:7b", "mistral", "gemma2", "personalizado"],
                index=0,
                help="Certifique-se de que o modelo foi baixado no Ollama (ex: ollama pull llama3.1)."
            )
            if ollama_model == "personalizado":
                ollama_model = st.text_input("Digite o nome do modelo:", value="llama3")
            
            st.info("💡 Dica: O Ollama deve estar rodando localmente.")
        
        with st.expander("🛠️ Ferramentas MCP (Opcional)"):
            tavily_key = st.text_input("Tavily/Brave API Key:", value=os.getenv("TAVILY_API_KEY", ""), type="password")
            if tavily_key:
                os.environ["TAVILY_API_KEY"] = tavily_key
            st.caption("Ativa pesquisa web profunda para os agentes.")
        
        st.header("✉️ Credenciais de Disparo (Canal 1)")
        sender_email = st.text_input("Seu E-mail (Gmail/Workspace):", value=default_email, placeholder="seuemail@gmail.com")
        sender_password = st.text_input("Senha de App (Google):", value=default_password, type="password")
        
        st.header("🔎 Arsenal de Prospecção")
        strategy = st.radio(
            "Selecione o Motor:",
            [
                "1. Radar de Licitações (Automático)",
                "2. Sniper B2B de Nicho (Automático)",
                "3. Raio-X de CNPJ (Manual)"
            ]
        )
        
        search_term = ""
        cnpj_target = ""
        
        if strategy == "2. Sniper B2B de Nicho (Automático)":
            search_term = st.text_input("Qual nicho e região?", value="Transportadora em Uberlândia")
        elif strategy == "3. Raio-X de CNPJ (Manual)":
            cnpj_target = st.text_input("Digite o CNPJ (somente números):")
    
    return ai_provider, api_key, ollama_model, sender_email, sender_password, strategy, search_term, cnpj_target


def render_header():
    """
    Renderiza o cabeçalho principal da aplicação
    """
    st.title("🎯 Motor SDR Autônomo - Next Tier Up (Modo Batching)")
    st.markdown(
        """
        Inteligência comercial e prospecção automatizadas com IA.
        
        **Como funciona:**
        1. Selecione uma estratégia de extração de leads
        2. Clique em "Iniciar Caçada em Lote" para processar
        3. A IA analisará os leads e gerará cadências personalizadas
        4. Use o Terminal de Execução para disparar e-mails e mensagens
        """
    )


def render_extraction_button() -> bool:
    """
    Renderiza o botão de iniciar extração
    
    Returns:
        bool: True se o botão foi clicado
    """
    return st.button("🚀 Iniciar Caçada em Lote", use_container_width=True)


def render_processing_container():
    """
    Renderiza um container para feedback de processamento
    
    Returns:
        Container do Streamlit
    """
    return st.container()


def render_results(results: str):
    """
    Renderiza os resultados do processamento
    
    Args:
        results: String com os resultados
    """
    st.markdown("### 🧠 Relatório Mestre de Prospecção")
    st.info("Aqui estão todas as estratégias geradas em um único fluxo. Use o terminal abaixo para executar.")
    st.markdown(results)


def render_execution_terminal():
    """
    Renderiza o terminal de execução global com abas
    
    Returns:
        Tuple: (tab_email, tab_whatsapp, tab_linkedin)
    """
    st.markdown("---")
    st.markdown("### ⚡ Terminal de Execução Global")
    
    return st.tabs(["✉️ Disparo de E-mail", "📱 WhatsApp Automático", "💼 Busca Rápida LinkedIn"])


def render_email_tab(tab):
    """
    Renderiza a aba de disparo de e-mail
    
    Args:
        tab: Objeto da aba do Streamlit
    
    Returns:
        Tuple: (recipient_email, subject, body, button_clicked)
    """
    with tab:
        recipient_email = st.text_input("E-mail do Alvo:")
        subject = st.text_input("Assunto do E-mail:")
        body = st.text_area("Cole a Copy Gerada no Relatório Acima:", height=150)
        button_clicked = st.button("🚀 Disparar E-mail", use_container_width=True)
        
        return recipient_email, subject, body, button_clicked


def render_whatsapp_tab(tab):
    """
    Renderiza a aba de WhatsApp automático
    
    Args:
        tab: Objeto da aba do Streamlit
    
    Returns:
        Tuple: (phone_number, message)
    """
    with tab:
        phone_number = st.text_input("WhatsApp (Ex: 5534999999999):")
        message = st.text_area("Cole a copy de WhatsApp/Call:")
        
        if phone_number and message:
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
            st.markdown(f"👉 **[ABRIR WHATSAPP WEB COM A MENSAGEM]({whatsapp_url})**")
        
        return phone_number, message


def render_linkedin_tab(tab):
    """
    Renderiza a aba de busca rápida LinkedIn
    
    Args:
        tab: Objeto da aba do Streamlit
    
    Returns:
        str: Nome da empresa
    """
    with tab:
        company_name = st.text_input("Digite o nome da Empresa para buscar os decisores:")
        
        if company_name:
            query = f"CEO OR Diretor OR Sócio {urllib.parse.quote(company_name)}"
            linkedin_url = f"https://www.linkedin.com/search/results/people/?keywords={query}"
            st.markdown(f"👉 **[PESQUISAR DECISORES NO LINKEDIN]({linkedin_url})**")
        
        return company_name


def show_info_message(message: str):
    """
    Exibe uma mensagem informativa
    
    Args:
        message: Mensagem a exibir
    """
    st.info(message)


def show_success_message(message: str):
    """
    Exibe uma mensagem de sucesso
    
    Args:
        message: Mensagem a exibir
    """
    st.success(message)


def show_warning_message(message: str):
    """
    Exibe uma mensagem de aviso
    
    Args:
        message: Mensagem a exibir
    """
    st.warning(message)


def show_error_message(message: str):
    """
    Exibe uma mensagem de erro
    
    Args:
        message: Mensagem a exibir
    """
    st.error(message)


def show_spinner(message: str):
    """
    Exibe um spinner de carregamento
    
    Args:
        message: Mensagem a exibir
    
    Returns:
        Context manager para o spinner
    """
    return st.spinner(message)
