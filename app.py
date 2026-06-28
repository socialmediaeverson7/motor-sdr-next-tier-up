# --- BOTS DE EXTRAÇÃO (SEM CUSTO DE API) ---

def bot_pncp():
    hoje = datetime.now().strftime("%Y%m%d")
    url = f"https://pncp.gov.br/api/consulta/v1/contratos?dataInicial={hoje}&dataFinal={hoje}&pagina=1"
    try:
        resposta = requests.get(url, headers={'accept': 'application/json'}, timeout=15)
        leads = []
        if resposta.status_code == 200:
            for c in resposta.json().get('data', [])[:3]:
                if c.get('niFornecedor'):
                    leads.append({
                        "alvo": c.get('nomeRazaoSocialFornecedor'),
                        "contexto": f"Ganhou licitação hoje para: {c.get('objetoContrato', 'Serviços/Obras')}",
                        "sinal": "Vitória em Licitação Pública"
                    })
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro no Bot do PNCP: {e}")
        return []

def bot_osint_linkedin():
    dork = 'site:br.linkedin.com/in "CEO" OR "Diretor" "Uberlândia"'
    leads = []
    try:
        # Forçamos o backend HTML para tentar burlar o Cloudflare
        with DDGS() as ddgs:
            resultados = list(ddgs.text(dork, max_results=3, backend="html"))
            if not resultados:
                st.warning("⚠️ Firewall do buscador bloqueou a raspagem silenciosamente. O IP da nuvem foi barrado.")
            for r in resultados:
                leads.append({
                    "alvo": r.get('title', '').split('-')[0].strip(),
                    "contexto": f"Resumo: {r.get('body', '')} | Link: {r.get('href', '')}",
                    "sinal": "Mudança de cargo recente ou perfil ativo"
                })
        return leads
    except Exception as e:
        st.error(f"⚠️ Bloqueio no Radar LinkedIn (DDGS): {e}")
        return []

def bot_sniper_local():
    # Nova Arma: OpenStreetMap (Nominatim API) - Imune a bloqueios de nuvem!
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": "Clínica de Estética em Uberlândia",
        "format": "json",
        "limit": 3,
        "addressdetails": 1
    }
    # O cabeçalho personalizado é obrigatório no OpenStreetMap para não sermos bloqueados
    headers = {"User-Agent": "MotorSDR_NextTierUp_Bot/1.0"}
    
    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=10)
        leads = []
        if resposta.status_code == 200:
            dados = resposta.json()
            for r in dados:
                nome_fantasia = r.get('display_name', '').split(',')[0]
                leads.append({
                    "alvo": nome_fantasia,
                    "contexto": f"Endereço físico confirmado via satélite/mapa: {r.get('display_name', '')}",
                    "sinal": "Negócio local operando com sede física na região"
                })
        else:
            st.error(f"⚠️ Erro HTTP Nominatim: {resposta.status_code}")
            
        return leads
    except Exception as e:
        st.error(f"⚠️ Erro no Sniper Local (Nominatim): {e}")
        return []
