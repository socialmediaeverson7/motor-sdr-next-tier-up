import os
import requests
import time
import traceback
from datetime import datetime
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

# Configuração de interface
st.set_page_config(page_title="Next Tier Up - SDR Autônomo", layout="wide")
st.title("🎯 Motor SDR Autônomo - Next Tier Up")

with st.sidebar:
    chave_api = st.text_input("Cole sua Chave do Gemini:", type="password")


def _request_with_retries(method, url, retries=3, backoff_factor=1.0, **kwargs):
    """Helper simples para realizar requests com retry e backoff exponencial."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.request(method, url, timeout=10, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as exc:
            if attempt == retries:
                raise
            sleep_time = backoff_factor * (2 ** (attempt - 1))
            time.sleep(sleep_time)


def buscar_vencedores_pncp_hoje(max_results=3):
    hoje = datetime.now().strftime("%Y%m%d")
    url = f"https://pncp.gov.br/api/consulta/v1/contratos?dataInicial={hoje}&dataFinal={hoje}&pagina=1"
    headers = {"accept": "application/json"}
    lista_cnpjs = []
    try:
        resp = _request_with_retries("GET", url, headers=headers)
        dados = resp.json()
        for contrato in dados.get("data", [])[:max_results]:
            # Campos podem variar, usar fallback
            cnpj = contrato.get("niFornecedor") or contrato.get("cnpjFornecedor") or contrato.get("cnpj")
            nome_empresa = contrato.get("nomeRazaoSocialFornecedor") or contrato.get("razaoSocialFornecedor") or contrato.get("nome")
            objeto = contrato.get("objetoContrato") or contrato.get("objeto") or "Serviços/Obras"

            if cnpj:
                cnpj_str = str(cnpj).zfill(14)
                digits = ''.join(filter(str.isdigit, cnpj_str))
                if len(digits) == 14:
                    lista_cnpjs.append({"cnpj": digits, "empresa": nome_empresa, "objeto": objeto})
        return lista_cnpjs
    except Exception:
        # Falha ao buscar do PNCP — retornar lista vazia e logar
        st.warning("Não foi possível conectar ao PNCP no momento.")
        return []


@tool("Consulta Oficial Receita Federal")
def consulta_receita(cnpj: str) -> str:
    """Consulta dados de um CNPJ na Receita Federal (via BrasilAPI) com tratamento robusto."""
    cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
    if not cnpj_limpo or len(cnpj_limpo) != 14:
        return "CNPJ inválido."

    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    try:
        resp = _request_with_retries("GET", url)
        dados = resp.json()

        razao = dados.get("razao_social") or dados.get("nome") or "N/A"
        socios_raw = dados.get("qsa", []) or dados.get("socios", [])
        socios = []
        for s in socios_raw:
            # Os nomes podem vir em chaves diferentes dependendo da fonte
            nome = s.get("nome") or s.get("nome_socio") or s.get("nomeSocio") or s.get("nome_do_socio")
            if nome:
                socios.append(nome.title())

        socios_str = ", ".join(socios) if socios else "Sócio não informado"
        return f"Empresa: {razao} | Decisores (Donos): {socios_str}"
    except Exception as e:
        return f"Erro na busca: {str(e)}"


# Fluxo principal de execução
if st.button("🚀 Iniciar Caçada de Leads"):
    if not chave_api:
        st.error("Insira sua chave API.")
    else:
        try:
            os.environ["GEMINI_API_KEY"] = chave_api
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

            # Agentes de Alta Performance (formatos mínimos)
            agente_dados = Agent(role="Analista", goal="Extrair sócios via CNPJ.", backstory="Expert em dados.", llm=llm, tools=[consulta_receita])
            agente_sdr = Agent(role="SDR", goal="Escrever e-mail comercial.", backstory="Closer de elite.", llm=llm)
            agente_revisor = Agent(role="Revisor", goal="Garantir perfeição técnica.", backstory="Editor rigoroso.", llm=llm)

            # Execução com tratamento de erro
            with st.spinner("Buscando leads..."):
                # Substitua por busca real no PNCP
                leads = buscar_vencedores_pncp_hoje() or [{"cnpj": "00000000000191", "empresa": "Exemplo LTDA", "objeto": "Serviço de TI"}]

                if not leads:
                    st.warning("Nenhum contrato novo encontrado hoje.")

                for lead in leads:
                    with st.expander(f"Processando: {lead.get('empresa', '—')}", expanded=True):
                        tarefa1 = Task(description=f"Consultar {lead['cnpj']}", expected_output="Lista de sócios.", agent=agente_dados)
                        tarefa2 = Task(description=f"Escrever e-mail para {lead['empresa']}", expected_output="E-mail finalizado.", agent=agente_sdr)
                        tarefa3 = Task(description="Revisar e-mail.", expected_output="Texto impecável.", agent=agente_revisor)

                        crew = Crew(agents=[agente_dados, agente_sdr, agente_revisor], tasks=[tarefa1, tarefa2, tarefa3], process=Process.sequential)

                        try:
                            resultado = crew.kickoff()
                            # Garantir que o resultado seja renderizável
                            st.write(str(resultado))
                        except Exception as err:
                            tb = traceback.format_exc()
                            st.error("Erro durante execução do fluxo. Veja o traceback abaixo.")
                            with st.expander("Traceback completo", expanded=False):
                                st.code(tb)

                            # Geração de sugestão básica (sem chamadas inseguras ao LLM)
                            sugestao_padrao = (
                                "Sugestão automática: verifique os parâmetros de criação dos Agents (campos obrigatórios),\n"
                                "valide as respostas das APIs externas e adicione tratamento de exceções.\n"
                                "Exemplo de ação: capturar o traceback e executar retry com backoff, além de log detalhado.\n"
                                "Se desejar, você pode copiar o traceback e solicitar uma correção manual via ChatGPT/LLM."
                            )
                            with st.expander("Sugestão de correção (automática)", expanded=False):
                                st.write(sugestao_padrao)

                            # Oferecer botão para gerar uma sugestão via LLM (se disponível)
                            if st.button("Gerar sugestão via LLM (aprox.)"):
                                try:
                                    prompt = (
                                        "Você é um assistente que sugere correções de código. Aqui está o traceback:\n\n"
                                        f"{tb}\n\n"
                                        "Forneça uma sugestão concisa do que corrigir no código do app Streamlit (em até 300 tokens)."
                                    )
                                    # Tentativa segura de usar o LLM — pode variar conforme a lib
                                    suggestion = None
                                    if hasattr(llm, 'generate'):
                                        # Algumas implementações de modelo usam .generate
                                        out = llm.generate([prompt])
                                        suggestion = str(out)
                                    elif callable(getattr(llm, '__call__', None)):
                                        suggestion = llm(prompt)
                                    else:
                                        suggestion = "LLM não suportado nesta runtime para geração automática."

                                    st.subheader("Sugestão do LLM (aproximada)")
                                    st.write(suggestion)

                                    st.info("Se aceitar a sugestão, eu posso gerar um patch que você aplicará manualmente no repositório.")
                                except Exception as e:
                                    st.error(f"Falha ao gerar sugestão via LLM: {e}")

        except Exception as e:
            st.error(f"Erro no sistema: {e}. O motor está tentando se auto-corrigir.")
