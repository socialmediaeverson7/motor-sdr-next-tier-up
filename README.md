# Motor SDR Autônomo - Next Tier Up (v2.0)

## 📋 Visão Geral

O **Motor SDR Autônomo** é uma aplicação inteligente de prospecção e geração de cadências de vendas que utiliza IA (Google Gemini) para automatizar o processo de Sales Development Representative (SDR). A aplicação extrai leads de múltiplas fontes, analisa dados comerciais e gera cadências omnichannel personalizadas (e-mail, LinkedIn, chamada).

### Principais Características

- **Múltiplas Estratégias de Extração**: Licitações públicas (PNCP), busca por nicho (OpenStreetMap), dados de CNPJ (ReceitaWS)
- **Análise Inteligente com IA**: Utiliza Google Gemini para análise de dados e geração de cadências
- **Processamento em Lote**: Processa múltiplos leads simultaneamente com eficiência
- **Interface Intuitiva**: Interface Streamlit amigável e responsiva
- **Integração Omnichannel**: Suporte para e-mail, WhatsApp e LinkedIn
- **Código Modularizado**: Arquitetura limpa e fácil de manter

---

## 🏗️ Arquitetura e Estrutura

### Estrutura de Diretórios

```
motor-sdr-refactored/
├── app.py                    # Aplicação principal
├── requirements.txt          # Dependências Python
├── .env.example             # Template de variáveis de ambiente
├── README.md                # Este arquivo
│
├── config/
│   ├── __init__.py
│   └── settings.py          # Configurações e constantes
│
└── modules/
    ├── __init__.py
    ├── ui.py                # Interface do usuário (Streamlit)
    ├── extraction_bots.py   # Bots de extração de leads
    ├── ai_agents.py         # Agentes de IA (CrewAI)
    ├── email_service.py     # Serviço de envio de e-mails
    └── utils.py             # Funções utilitárias
```

### Módulos Principais

#### `config/settings.py`
Centraliza todas as configurações, constantes, prompts e templates da aplicação. Facilita ajustes sem modificar o código principal.

#### `modules/ui.py`
Implementa todos os componentes da interface Streamlit, separando a lógica de apresentação da lógica de negócio.

#### `modules/extraction_bots.py`
Define três bots de extração:
- **PNCPBot**: Extrai licitações públicas recentes
- **SniperNichoBot**: Busca empresas por nicho e região
- **OSINTReceitaBot**: Obtém dados detalhados via CNPJ

#### `modules/ai_agents.py`
Gerencia os agentes CrewAI:
- **Data Analyst Agent**: Analisa lotes de empresas
- **SDR Agent**: Gera cadências omnichannel personalizadas

#### `modules/email_service.py`
Implementa o serviço de envio de e-mails com validação robusta e tratamento de erros.

#### `modules/utils.py`
Funções utilitárias para validação, formatação e manipulação de dados.

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- pip ou pip3
- Conta Google com acesso à API Gemini
- Conta Gmail com senha de app configurada

### Passo 1: Clonar ou Baixar o Repositório

```bash
git clone <seu-repositorio>
cd motor-sdr-refactored
```

### Passo 2: Criar um Ambiente Virtual (Recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar Variáveis de Ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### Passo 5: Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`

---

## 📖 Guia de Uso

### 1. Configuração Inicial

Na barra lateral, preencha:

- **Chave de IA**: Cole sua chave de API do Google Gemini
- **Credenciais de Disparo**: E-mail e senha de app do Gmail
- **Arsenal de Prospecção**: Selecione a estratégia de extração

### 2. Seleção de Estratégia

**Opção 1: Radar de Licitações (Automático)**
- Extrai licitações públicas do dia
- Não requer entrada adicional

**Opção 2: Sniper B2B de Nicho (Automático)**
- Busca empresas por nicho e região
- Exemplo: "Transportadora em Uberlândia"

**Opção 3: Raio-X de CNPJ (Manual)**
- Obtém dados detalhados de uma empresa
- Requer CNPJ válido (14 dígitos)

### 3. Iniciar Caçada em Lote

Clique em **"🚀 Iniciar Caçada em Lote"** para:
1. Extrair leads
2. Analisar dados comerciais
3. Gerar cadências omnichannel

### 4. Terminal de Execução

#### Aba de E-mail
- Insira o e-mail do alvo
- Digite o assunto
- Cole a copy gerada
- Clique em "Disparar E-mail"

#### Aba de WhatsApp
- Insira o número (formato: 55XXXXX)
- Cole a mensagem
- Clique no link gerado para abrir WhatsApp Web

#### Aba de LinkedIn
- Insira o nome da empresa
- Clique no link para buscar decisores

---

## 🔧 Melhorias Implementadas (v2.0)

### 1. Modularização
- Código separado em módulos lógicos
- Fácil manutenção e extensão
- Reuso de componentes

### 2. Tratamento de Erros
- Exceções customizadas
- Mensagens de erro claras
- Validação robusta de entradas

### 3. Otimização de Prompts
- Prompts mais detalhados e específicos
- Melhor estruturação de respostas da IA
- Templates centralizados

### 4. Gerenciamento de Estado
- Session state do Streamlit
- Persistência de dados durante a sessão
- Melhor experiência do usuário

### 5. Validação de Dados
- Validação de e-mail
- Validação de CNPJ
- Validação de chaves de API

### 6. Documentação
- Docstrings em todas as funções
- Comentários explicativos
- README completo

---

## 🔐 Segurança

### Boas Práticas Implementadas

1. **Variáveis de Ambiente**: Credenciais armazenadas em `.env`
2. **Inputs Sensíveis**: Campos de senha mascarados
3. **Validação de Entrada**: Todos os inputs são validados
4. **Tratamento de Erros**: Erros não expõem informações sensíveis
5. **Telemetria Desabilitada**: CrewAI e LangChain telemetry desabilitados

### Recomendações

- Nunca compartilhe suas chaves de API
- Use senhas de app do Google, não a senha da conta
- Mantenha o arquivo `.env` fora do controle de versão
- Revise regularmente as permissões das APIs

---

## 📊 Exemplos de Uso

### Exemplo 1: Prospecção de Licitações

```
1. Selecione "Radar de Licitações"
2. Clique em "Iniciar Caçada em Lote"
3. A IA analisará as licitações do dia
4. Gere cadências para as empresas vencedoras
5. Dispare e-mails personalizados
```

### Exemplo 2: Busca por Nicho

```
1. Selecione "Sniper B2B de Nicho"
2. Digite "Agência de Marketing em São Paulo"
3. Clique em "Iniciar Caçada em Lote"
4. Revise as cadências geradas
5. Use LinkedIn para encontrar decisores
```

### Exemplo 3: Análise de Empresa

```
1. Selecione "Raio-X de CNPJ"
2. Digite um CNPJ válido
3. Clique em "Iniciar Caçada em Lote"
4. Analise os dados da empresa
5. Crie uma abordagem personalizada
```

---

## 🐛 Troubleshooting

### Erro: "Chave de API do Gemini não fornecida"
- Verifique se você inseriu a chave corretamente
- A chave não pode estar vazia

### Erro: "E-mail do remetente inválido"
- Verifique o formato do e-mail
- Certifique-se de usar um e-mail Gmail válido

### Erro: "Erro de autenticação SMTP"
- Use uma senha de app do Google, não a senha da conta
- Ative a autenticação de dois fatores no Google
- Gere uma nova senha de app

### Erro: "CNPJ não encontrado"
- Verifique se o CNPJ está correto (14 dígitos)
- Certifique-se de que a empresa existe
- Tente novamente em alguns momentos

### Erro: "Nenhum alvo encontrado"
- Verifique o termo de busca
- Tente um termo mais genérico
- Verifique a conexão com a internet

---

## 📈 Roadmap Futuro

- [ ] Integração com LinkedIn Sales Navigator
- [ ] Busca de notícias e eventos recentes
- [ ] Extração de dados de websites
- [ ] Banco de dados local para histórico
- [ ] Análise de sentimento em respostas
- [ ] Agendamento automático de follow-ups
- [ ] Exportação de relatórios em PDF
- [ ] Integração com CRM (Pipedrive, HubSpot)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

---

## 👨‍💻 Autor

Desenvolvido com ❤️ por **Manus AI**

---

## 📞 Suporte

Para suporte, abra uma issue no repositório ou entre em contato através de [seu-email@exemplo.com].

---

## 🙏 Agradecimentos

- Google Gemini pela IA poderosa
- CrewAI pela orquestração de agentes
- Streamlit pela interface intuitiva
- PNCP, OpenStreetMap e ReceitaWS pelas APIs públicas

---

**Versão**: 2.0 (Refatorada)  
**Última Atualização**: Junho 2024  
**Status**: Ativo e em desenvolvimento
