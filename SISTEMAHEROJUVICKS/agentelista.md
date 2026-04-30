# 🧠 MASTER SYSTEM ARCHITECTURE: JUVIKS SERVER (agentelista.md)

Este documento é a **Bússola de Engenharia** do sistema. Ele define a hierarquia, os fluxos de dados e as responsabilidades de cada módulo. Qualquer Agente de IA deve consultar este arquivo antes de realizar alterações para garantir a integridade do "Ecossistema Juviks".

---

## 🏗️ 1. ESTRUTURA DE DIRETÓRIOS E FLUXO DE DADOS

O sistema opera sob uma arquitetura de **Microserviços Orquestrados**:

### 📂 Diretórios Raiz
- `PY/`: Núcleo Python. Contém o `launcher.py` (Orquestrador) e subpastas de lógica.
- `PY/pages/`: Interface Streamlit. Cada arquivo é uma página do ERP/CRM.
- `PY/WHATSAPP_MOTOR/`: Microserviço Node.js para automação de mensagens.
- `DATABASE/`: Armazenamento persistente (SQLite). **CRÍTICO:** No modo EXE, este diretório deve ser tratado como externo ou espelhado em `%LOCALAPPDATA%`.
- `ICONE/` & `MODELOS_HTML/`: Recursos visuais e templates de documentos.

### 🔄 Fluxo de Inicialização (Launcher)
1. **Lançador (`launcher.py`)**: Verifica porta 8501 e 5001. Se livres, inicia.
2. **Motor Streamlit**: Sobe o `PY/Inicio.py` na porta 8501.
3. **Motor Flask**: Sobe o `assiname_app/app.py` na porta 5001 (Assinaturas).
4. **Motor Node.js**: Sobe `gateway.js` (WhatsApp) via `node.exe` embutido.
5. **Tray Icon**: Mantém o controle visual e permite desligar todos os processos via "Stop Nuclear".

---

## 🛠️ 2. MÓDULOS DE NEGÓCIO (SOP - Standard Operating Procedures)

| Módulo | Arquivo Principal | Dependência Chave | Função |
| :--- | :--- | :--- | :--- |
| **CRM** | `1_1-Clientes.py` | `database.py` | Gestão de Leads e Clientes. |
| **Financeiro** | `12_12-Financeiro.py` | `sqlite3` | Fluxo de caixa e faturamento. |
| **Orçamentos** | `3_3-Gerar_Orcamentos.py`| `fpdf` / `MODELOS_HTML` | Geração de PDFs profissionais. |
| **WhatsApp** | `97_Configuracao_Zap.py` | `WHATSAPP_MOTOR` | Interface de pareamento e disparos. |
| **Assinaturas** | `8_8-Assinaturas.py` | `Flask (Port 5001)` | Colhe assinaturas em contratos. |
| **SaaS/Licença**| `saas_manager.py` | `HWID` / `HUB Master` | Controle de acesso e expiração. |

---

## 🔐 3. REGRAS DE OURO PARA O AGENTE (PREVENÇÃO DE ERROS)

1. **Path Integrity**: Sempre use `os.path.join`. Para caminhos relativos ao EXE, use o `sys._MEIPASS` se `sys.frozen` for True, mas para **DADOS (DB/Logs)**, use sempre caminhos relativos ao `sys.executable` ou `%LOCALAPPDATA%`.
2. **Process Management**: O sistema usa `subprocess.Popen`. Nunca deixe processos órfãos. Use o `stop_all` do `launcher.py` como referência para limpeza.
3. **Portas Estáticas**: 
   - Streamlit: `8501`
   - Flask: `5001`
   - Node Gateway: `8080` (Interno)
4. **Encoding**: Todo script deve salvar em `UTF-8`. Arquivos `.md` e `.py` devem ser revisados para evitar caracteres corrompidos no terminal Windows.
5. **SaaS Consistency**: O HWID do cliente deve ser validado no `saas_manager.py` antes de liberar as páginas da pasta `/pages`.

---

## 🚀 4. OBJETIVO DO EXECUTÁVEL "PERFEITO"
Um build perfeito deve:
- Ser **Stand-alone**: Incluir `node.exe` e `ngrok.exe`.
- Ser **Resiliente**: Detectar se as portas estão ocupadas e oferecer limpeza.
- Ser **Persistente**: Não perder os dados do `DATABASE` ao fechar (resolver conflito de pastas temporárias).

> **Assinatura de Integridade:** Este guia é a versão final e estável. Mudanças na estrutura de pastas devem ser refletidas aqui imediatamente.

