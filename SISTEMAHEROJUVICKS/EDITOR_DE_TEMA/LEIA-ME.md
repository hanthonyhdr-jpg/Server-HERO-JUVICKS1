# 🎨 Editor de Tema Visual — JUVIKS07

Aplicativo standalone para editar o design do sistema JUVIKS07 sem precisar mexer em código.

## 📁 Localização
```
SISTEMAJUV/
└── EDITOR_DE_TEMA/
    ├── editor_tema.py         ← App principal
    ├── ABRIR_EDITOR_TEMA.bat  ← Clique duas vezes para abrir
    ├── backups/               ← Backups criados automaticamente
    └── LEIA-ME.md             ← Este arquivo
```

## 🚀 Como Usar

### Opção 1 — Clique Duplo (Recomendado)
Dê dois cliques em **`ABRIR_EDITOR_TEMA.bat`**  
O editor abre no navegador em `http://localhost:8599`

### Opção 2 — Terminal
```bash
cd EDITOR_DE_TEMA
..\venv\Scripts\streamlit run editor_tema.py --server.port=8599
```

---

## 🎨 Funcionalidades

### 🖌️ Aba 1 — Cores
- **Color pickers visuais** para todas as cores do sistema
- **Preview em tempo real** simulando o layout do sistema
- Cores editáveis:
  - Fundo Principal e Externo
  - Acento Principal (botões, links, destaques)
  - Acento Secundário (hover, glow)
  - Sidebar (cor e borda)
  - Cards (fundo e borda)
  - Texto Principal e Secundário

### 📐 Aba 2 — Layout & Efeitos
- Raio das bordas (cards, botões, inputs)
- Intensidade do Blur (Glassmorphism)
- Opacidade das sombras
- **Troca de fonte** (Outfit, Inter, Roboto, Poppins, etc.)

### 📝 Aba 3 — Editor de Código Direto
- Edite o `moderno.py` diretamente no browser
- Backup automático antes de qualquer salvamento

### 💾 Aba 4 — Backups
- Histórico de todas as versões anteriores do tema
- Download individual de qualquer backup
- Restauração com 1 clique
- Limpeza automática (mantém os 10 mais recentes)

---

## ⚠️ Importante
- O editor edita diretamente o arquivo `PY/TEMAS/moderno.py`
- Sempre é criado um backup automático antes de salvar
- Para restaurar o original, use a aba **Backups**
