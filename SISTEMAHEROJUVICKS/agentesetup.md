# 🛠️ PROTOCOLO DE COMPILAÇÃO E DEPLOY (agentesetup.md)

Este documento define o **Workflow Obrigatório** para gerar a versão de produção do **JUVIKS SERVER**. Seguir este protocolo elimina erros de "Startup Crash" e garante a portabilidade total.

---

## 🚀 1. PRÉ-REQUISITOS DE AMBIENTE (CHECKLIST)
Antes de iniciar a compilação (Opção 11), valide:
- [ ] **Python 3.10+** no `venv/`.
- [ ] **Bibliotecas Críticas**: `streamlit`, `flask`, `pystray`, `pyinstaller`, `pillow`.
- [ ] **Binários Externos**: `ngrok.exe` na raiz e `node.exe` dentro de `PY/WHATSAPP_MOTOR/`.
- [ ] **Inno Setup 6**: Instalado no Windows (necessário para o `.iss`).

---

## 🏗️ 2. O FLUXO DE BUILD (PASSO A PASSO)

### Passo 0: Limpo de Fábrica (Obrigatório para Versão Final)
Antes de compilar a versão que irá para o cliente, você deve garantir que o sistema não leve dados de teste:
1.  Execute o script de limpeza: `python scratch/reset_fabrica.py`.
2.  Certifique-se de que a pasta `dist/` foi apagada.
3.  Verifique se o `db_config.json` está com as credenciais de produção (ou SQLite se for versão local).

### Passo 1: Higienização de Dados
O script `compilar_sistema.py` deve ser executado para:
1. Remover `license.key` e pastas de `sessions` (Privacidade do Cliente).
2. Limpar builds antigos (`build/`, `dist/`).
3. Verificar se o `node.exe` está presente para injeção.

### Passo 2: Execução do PyInstaller
O comando principal deve ser:
```powershell
.\venv\Scripts\python.exe compilar_sistema.py
```
**Atenção:** Se houver erro de recursão, edite o `SISTEMA_JUVIKS_OFICIAL.spec` e adicione `import sys; sys.setrecursionlimit(2000)` no topo.

### Passo 3: Empacotamento Inno Setup
O `compilar_sistema.py` invocará o `ISCC.exe`. O instalador deve ser gerado na pasta `Output/`.

---

## 🐞 3. RESOLUÇÃO DE ERROS COMUNS (TROUBLESHOOTING)

| Sintoma | Causa Provável | Solução |
| :--- | :--- | :--- |
| **Erro ao Iniciar EXE** | Falta de módulos em `hiddenimports`. | Adicionar o módulo faltante no `.spec` e recompilar. |
| **Tela Branca / Freeze** | Porta 8501 ou 5001 ocupada. | Usar "Opção 2" do Painel para matar processos órfãos. |
| **Banco de Dados Reseta** | DB está sendo gravado em pasta temp. | Ajustar `launcher.py` para usar caminho absoluto fora do `_MEIPASS`. |
| **WhatsApp não conecta** | `node.exe` não encontrado. | Garantir que `node.exe` está em `PY/WHATSAPP_MOTOR/`. |

---

## ✅ 4. CRITÉRIOS DE "EXECUTÁVEL PERFEITO"
A entrega só é válida se:
1. O sistema abre o **Tray Icon** e o **Navegador** automaticamente.
2. O **Splash Screen** mostra o progresso sem travar.
3. Ao fechar o sistema pelo ícone da bandeja, **todos os processos** (Python, Node, Ngrok) são encerrados.
4. Os dados salvos no `DATABASE` permanecem lá após reiniciar o PC.

---
**Ultima Revisão:** 22/04/2026
**Responsável:** Antigravity (IA Lead)

