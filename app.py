"""
Motor SDR Autônomo - Next Tier Up (Modo Batching)
Aplicação principal de prospecção e geração de cadências com IA
"""

import sys
import types

# ============================================================================
# BYPASS DE MÓDULOS E CONFIGURAÇÃO INICIAL
# ============================================================================

# Mock para pkg_resources (necessário para compatibilidade)
if "pkg_resources" not in sys.modules:
    mock_pkg = types.ModuleType("pkg_resources")
    mock_pkg.get_distribution = lambda x: types.SimpleNamespace(version="0.0.0")
    sys.modules["pkg_resources"] = mock_pkg

# ============================================================================
# IMPORTS
# ============================================================================

import streamlit as st
from modules import ui
from modules.extraction_bots import get_leads_by_strategy, LeadExtractionError
from modules.ai_agents import validate_and_initialize_ai, AIAgentError
from modules.email_service import send_email_safely
from modules.utils import format_leads_for_batch
from config.settings import MESSAGES

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

ui.configure_page()

# ============================================================================
# INICIALIZAÇÃO DE SESSION STATE
# ============================================================================

if "processing" not in st.session_state:
    st.session_state.processing = False

if "last_results" not in st.session_state:
    st.session_state.last_results = None

if "processed_targets" not in st.session_state:
    st.session_state.processed_targets = set()

# ============================================================================
# RENDERIZAÇÃO DA INTERFACE
# ============================================================================

ui.render_header()

# Renderizar sidebar e obter inputs
ollama_model, sender_email, sender_password, strategy, search_term, cnpj_target = ui.render_sidebar()

# Renderizar botão de iniciar caçada
if ui.render_extraction_button():
    st.session_state.processing = True

# ============================================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================================

if st.session_state.processing:
    processing_container = ui.render_processing_container()
    
    try:
        # 1. Inicializar IA (Ollama Local)
        with st.status("🧠 Inicializando Cérebro da IA (Ollama Local)...", expanded=False) as status:
            ai_manager = validate_and_initialize_ai(
                ollama_model=ollama_model
            )
            if not ai_manager:
                st.session_state.processing = False
                st.stop()
            status.update(label="✅ IA Pronta!", state="complete")
        
        # 2. Extrair leads baseado na estratégia selecionada
        with ui.show_spinner("Extraindo lote de alvos..."):
            strategy_map = {
                "1. Radar de Licitações (Automático)": "pncp",
                "2. Sniper B2B de Nicho (Automático)": "sniper",
                "3. Raio-X de CNPJ (Manual)": "cnpj"
            }
            
            strategy_key = strategy_map.get(strategy, "pncp")
            
            if strategy_key == "sniper":
                leads = get_leads_by_strategy(strategy_key, search_term=search_term)
            elif strategy_key == "cnpj":
                leads = get_leads_by_strategy(strategy_key, cnpj=cnpj_target)
            else:
                leads = get_leads_by_strategy(strategy_key)
            
            # Filtrar alvos já processados
            leads = [l for l in leads if l['alvo'] not in st.session_state.processed_targets]
        
        # Validar se há leads
        if not leads:
            ui.show_warning_message(MESSAGES["warning_no_leads"])
            st.session_state.processing = False
            st.stop()
        
        # Informar quantidade de leads
        ui.show_info_message(MESSAGES["info_batch_ready"].format(count=len(leads)))
        
        # Formatar leads para processamento
        batch_text = format_leads_for_batch(leads)
        
        # 3. Processar lote com IA
        with ui.show_spinner("Processando cadências via Ollama Local..."):
            results = ai_manager.process_batch(batch_text)
            st.session_state.last_results = results
        
        # 4. Renderizar resultados
        if results:
            ui.render_results(results)
            # Adicionar alvos ao histórico de processados
            for lead in leads:
                st.session_state.processed_targets.add(lead['alvo'])
        
        st.session_state.processing = False
        
    except LeadExtractionError as e:
        ui.show_error_message(f"Erro na extração de leads: {e}")
        st.session_state.processing = False
    except AIAgentError as e:
        ui.show_error_message(f"Erro na IA: {e}")
        st.session_state.processing = False
    except Exception as e:
        ui.show_error_message(f"Erro inesperado: {e}")
        st.session_state.processing = False

# ============================================================================
# TERMINAL DE EXECUÇÃO GLOBAL
# ============================================================================

tab_email, tab_whatsapp, tab_linkedin = ui.render_execution_terminal()

# --- ABA DE E-MAIL ---
recipient_email, subject, body, email_button_clicked = ui.render_email_tab(tab_email)

if email_button_clicked:
    success = send_email_safely(sender_email, sender_password, recipient_email, subject, body)

# --- ABA DE WHATSAPP ---
phone_number, whatsapp_message = ui.render_whatsapp_tab(tab_whatsapp)

# --- ABA DE LINKEDIN ---
company_name = ui.render_linkedin_tab(tab_linkedin)

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 12px;">
    Motor SDR v2.0 | Desenvolvido com ❤️ por Manus AI
    </div>
    """,
    unsafe_allow_html=True
)
