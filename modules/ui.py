"""
Módulo de Interface do Usuário (Streamlit)
Focado no uso do Ollama Local para independência total de APIs externas
"""

import streamlit as st
import os
from typing import Tuple, Optional


def configure_page():
    """Configura as definições básicas da página Streamlit"""
    st.set_page_config(
        page_title="Motor SDR v2.0 - Next Tier Up",
        page_icon="🚀",
        layout="wide"
    )


def render_sidebar() -> Tuple[str, str, str, str, str, str]:
    """
    Renderiza a barra lateral e retorna as configurações do usuário
    """
    with st.sidebar:
        st.header("⚙️ Configuração de IA")
        
        st.success("⚡ Modo Ollama Local Ativo")
        
        ollama_model = st.selectbox(
            "Selecione o Modelo Ollama:",
            ["llama3.1:8b", "qwen2.5-coder:7b", "mistral", "gemma2", "personalizado"],
            index=0,
            help="Certifique-se de que o modelo foi baixado no Ollama (ex: ollama pull llama3.1:8b)."
        )
        
        if ollama_model == "personalizado":
            ollama_model = st.text_input("Digite o nome exato do modelo:", value="llama3.1:8b")
        
        st.info("💡 Dica: O Ollama deve estar aberto na sua máquina.")

        st.header("🛠️ Ferramentas MCP (Opcional)")
        with st.expander("Configurar Pesquisa Web"):
            tavily_key = st.text_input("Tavily/Brave API Key:", value=os.getenv("TAVILY_API_KEY", ""), type="password")
            if tavily_key:
                os.environ["TAVILY_API_KEY"] = tavily_key
            st.caption("Deixe em branco para usar DuckDuckGo (Grátis).")

        st.header("✉️ Credenciais de Disparo")
        sender_email = st.text_input("Seu E-mail (Gmail/Workspace):", value=os.getenv("SENDER_EMAIL", ""), placeholder="seuemail@gmail.com")
        sender_password = st.text_input("Senha de App (Google):", value=os.getenv("SENDER_PASSWORD", ""), type="password")

        st.header("🎯 Estratégia de Extração")
        strategy = st.radio(
            "Escolha a fonte dos leads:",
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
    
    return ollama_model, sender_email, sender_password, strategy, search_term, cnpj_target


def render_header():
    """Renderiza o cabeçalho da aplicação"""
    st.title("🚀 Motor SDR v2.0 - Next Tier Up")
    st.subheader("Inteligência Comercial Autônoma e Local (100% Offline via Ollama)")
    st.markdown("---")


def render_extraction_button() -> bool:
    """Renderiza o botão de iniciar caçada"""
    return st.button("🚀 Iniciar Caçada em Lote", use_container_width=True)


def render_processing_container():
    """Cria um container para exibir o progresso do processamento"""
    return st.empty()


def show_spinner(text: str):
    """Exibe um spinner de carregamento"""
    return st.spinner(text)


def show_info_message(text: str):
    """Exibe uma mensagem informativa"""
    st.info(text)


def show_warning_message(text: str):
    """Exibe uma mensagem de aviso"""
    st.warning(text)


def show_error_message(text: str):
    """Exibe uma mensagem de erro"""
    st.error(text)


def render_results(results: str):
    """Renderiza os resultados do processamento"""
    st.markdown("### 🎯 Relatório de Inteligência e Cadências")
    st.markdown(results)
    st.download_button(
        label="📥 Baixar Relatório (Markdown)",
        data=results,
        file_name="relatorio_sdr.md",
        mime="text/markdown"
    )


def render_execution_terminal():
    """Renderiza o terminal de execução para disparo de mensagens"""
    st.markdown("---")
    st.markdown("### ⚡ Terminal de Execução")
    return st.tabs(["📧 E-mail Marketing", "💬 WhatsApp Sniper", "🔗 LinkedIn Connect"])


def render_email_tab(tab):
    """Renderiza a aba de e-mail"""
    with tab:
        col1, col2 = st.columns(2)
        with col1:
            recipient = st.text_input("E-mail do Destinatário:", placeholder="contato@empresa.com")
            subject = st.text_input("Assunto:", value="Oportunidade de Otimização")
        with col2:
            body = st.text_area("Corpo do E-mail:", height=200)
        
        btn = st.button("📧 Disparar E-mail agora")
        return recipient, subject, body, btn


def render_whatsapp_tab(tab):
    """Renderiza a aba de WhatsApp"""
    with tab:
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("WhatsApp (com DDD):", placeholder="34999999999")
        with col2:
            msg = st.text_area("Mensagem:", height=150)
        
        if st.button("💬 Abrir no WhatsApp Web"):
            url = f"https://web.whatsapp.com/send?phone=55{phone}&text={msg}"
            st.markdown(f'<a href="{url}" target="_blank">Clique aqui para enviar</a>', unsafe_allow_html=True)
        return phone, msg


def render_linkedin_tab(tab):
    """Renderiza a aba de LinkedIn"""
    with tab:
        company = st.text_input("Nome da Empresa para busca:")
        if st.button("🔗 Buscar Decisores no LinkedIn"):
            url = f"https://www.linkedin.com/search/results/people/?keywords={company}%20decisor"
            st.markdown(f'<a href="{url}" target="_blank">Ver resultados no LinkedIn</a>', unsafe_allow_html=True)
        return company
