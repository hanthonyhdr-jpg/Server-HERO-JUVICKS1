import streamlit as st
import os
import sys
import pandas as pd
import json
import base64
import sqlite3
from datetime import datetime
from fpdf import FPDF
from database import buscar_dados, executar_comando
from utils.query_cache import (
    cached_buscar_dados,
    get_financeiro_cache_version,
    bump_financeiro_cache_version,
    bump_orcamentos_cache_version,
)

# Adiciona a raiz do projeto ao sys.path
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from TEMAS.moderno import apply_modern_style
from utils.auth_manager import verificar_autenticacao, obter_dados_empresa, verificar_permissao_modulo, verificar_nivel_acesso, tem_permissao

# ─── CONFIG ────────────────────────────────────────────────────────────────────
empresa_nome, logo_src = obter_dados_empresa()
st.set_page_config(page_title=f"Financeiro | {empresa_nome}", layout="wide", page_icon="💰")
apply_modern_style(logo_url=logo_src, nome_empresa=empresa_nome)

verificar_autenticacao()
verificar_nivel_acesso(["ADMIN", "GERENTE", "VENDEDOR"])
verificar_permissao_modulo("Financeiro")
financeiro_cache_version = get_financeiro_cache_version()

# ─── UTILS ─────────────────────────────────────────────────────────────────────
def safe_loads(s, fallback=[]):
    if not s or s == 'null': return fallback
    try:
        if isinstance(s, list): return s
        return json.loads(s)
    except: return fallback

def get_val(row, key, default=0):
    """Acesso seguro a coluna de pandas Series, retorna default se None."""
    v = row.get(key, default)
    return v if v is not None else default

def renderizar_template(nome_arquivo, variaveis):
    """Lê um arquivo HTML da pasta MODELOS_HTML e substitui as variáveis."""
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MODELOS_HTML", nome_arquivo)
    if not os.path.exists(caminho):
        # Tenta caminho relativo à raiz do projeto se o acima falhar (depende da estrutura de pastas)
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        caminho = os.path.join(raiz, "MODELOS_HTML", nome_arquivo)
        
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            html = f.read()
        for chave, valor in variaveis.items():
            html = html.replace(f"{{{{{chave}}}}}", str(valor))
        return html
    except Exception as e:
        return f"<div style='color:red;'>Erro ao carregar template: {e}</div>"

@st.dialog("🚀 Dashboard Executivo", width="large")
def visualizar_dashboard_full(vars_dash):
    """Exibe o dashboard moderno em uma janela modal (Full Screen)."""
    html_dash = renderizar_template("dashboard_moderno.html", vars_dash)
    st.components.v1.html(html_dash, height=800, scrolling=True)
    if st.button("❌ Fechar Dashboard", use_container_width=True):
        st.rerun()

# ─── CSS EXTRA ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.fin-badge-pago    { background:#16a34a22;border:1px solid #16a34a;color:#22c55e;padding:3px 10px;border-radius:20px;font-size:.8rem;font-weight:700; }
.fin-badge-parcial { background:#d9770622;border:1px solid #d97706;color:#fbbf24;padding:3px 10px;border-radius:20px;font-size:.8rem;font-weight:700; }
.fin-badge-pend    { background:#dc264422;border:1px solid #dc2626;color:#f87171;padding:3px 10px;border-radius:20px;font-size:.8rem;font-weight:700; }
.fin-row           { display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1e2940; }
.fin-label         { color:#64748b;font-size:.9rem; }
.fin-value         { color:#f1f5f9;font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ─── TÍTULO ────────────────────────────────────────────────────────────────────
st.title("💰 Gerenciador Financeiro")
st.caption("Controle completo de custos, taxas, pagamentos e recebimentos por pedido.")

# ─── ABAS ──────────────────────────────────────────────────────────────────────
tab_dash, tab_entry, tab_records, tab_manage = st.tabs([
    "🚀 Painel Geral", 
    "💸 Registrar Movimento", 
    "📈 Extrato & Relatórios", 
    "⚙️ Gestão & Dados"
])

# ══════════════════════════════════════════════════════════════════════════
# ABA 1 — DASHBOARD ERP
# ══════════════════════════════════════════════════════════════════════════
with tab_dash:
    # Busca dados globais
    df_orc = cached_buscar_dados("SELECT total, custo_producao, valor_pago, valor_liquido FROM orcamentos WHERE status='Aprovado'", version=financeiro_cache_version)
    df_pro = cached_buscar_dados("SELECT valor_venda FROM projetos", version=financeiro_cache_version)
    df_gas = cached_buscar_dados("SELECT valor FROM gastos", version=financeiro_cache_version)
    df_ent = cached_buscar_dados("SELECT valor FROM entradas", version=financeiro_cache_version)

    # Cálculos rápidos
    fat_v = df_orc['total'].sum() if not df_orc.empty else 0
    rec_v = df_orc['valor_pago'].sum() if not df_orc.empty else 0
    cus_v = df_orc['custo_producao'].sum() if not df_orc.empty else 0
    
    vars_dash_global = {
        "FATURAMENTO": f"{fat_v:,.2f}",
        "RECEITA_LIQUIDA": f"{rec_v:,.2f}",
        "CUSTOS": f"{cus_v:,.2f}"
    }

    c_header1, c_header2 = st.columns([4, 1])
    with c_header1:
        st.subheader("🚀 Indicadores de Performance (ERP)")
    with c_header2:
        visual_moderno = st.toggle("🎨 Painel Moderno", value=False, key="toggle_modern_dash")
        if st.button("🖥️ Tela Cheia", key="btn_full_top", use_container_width=True):
            visualizar_dashboard_full(vars_dash_global)

    if visual_moderno:
        html_dash = renderizar_template("dashboard_moderno.html", vars_dash_global)
        st.components.v1.html(html_dash, height=750, scrolling=True)
    else:
        total_vendas_orc = df_orc['total'].sum() if not df_orc.empty else 0
        total_vendas_pro = df_pro['valor_venda'].sum() if not df_pro.empty else 0
        total_venda_geral = total_vendas_orc + total_vendas_pro
        
        total_recebido_orc = df_orc['valor_pago'].sum() if not df_orc.empty else 0
        total_recebido_ent = df_ent['valor'].sum() if not df_ent.empty else 0
        total_recebido_geral = total_recebido_orc + total_recebido_ent
        
        total_gastos_avulso = df_gas['valor'].sum() if not df_gas.empty else 0
        total_custo_prod    = df_orc['custo_producao'].sum() if not df_orc.empty else 0
        total_gastos_geral  = total_gastos_avulso + total_custo_prod
        
        lucro_total = total_venda_geral - total_gastos_geral
        
        cw1, cw2, cw3, cw4 = st.columns(4)
        cw1.metric("Faturamento Geral", f"R$ {total_venda_geral:,.2f}")
        cw2.metric("Total Recebido", f"R$ {total_recebido_geral:,.2f}")
        cw3.metric("Custos e Gastos", f"R$ {total_gastos_geral:,.2f}", delta_color="inverse")
        
        margem = (lucro_total / total_venda_geral * 100) if total_venda_geral > 0 else 0
        cw4.metric("Margem Projetada", f"{margem:.1f}%", delta=f"R$ {lucro_total:,.2f}")

    st.divider()
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        if not df_gas.empty:
            df_cat = cached_buscar_dados("SELECT categoria, SUM(valor) as total FROM gastos GROUP BY categoria", version=financeiro_cache_version)
            if not df_cat.empty:
                try:
                    import plotly.express as px
                    fig_cat = px.pie(df_cat, values='total', names='categoria', title='Distribuição de Gastos Avulsos', hole=.4)
                    fig_cat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e0f2fe", showlegend=False)
                    st.plotly_chart(fig_cat, use_container_width=True)
                except: st.info("Instale 'plotly' para ver gráficos.")

    with col_g2:
        from database import contar_registros
        st.info(f"""
        **Resumo Rápido:**
        - Projetos em Orçamento: **{contar_registros('orcamentos')}**
        - Projetos Manuais: **{contar_registros('projetos')}**
        - ÚLTIMA ENTRADA: **R$ {df_ent['valor'].iloc[0] if not df_ent.empty else 0:,.2f}**
        """)

# ══════════════════════════════════════════════════════════════════════════
# ABA 2 — REGISTRAR MOVIMENTAÇÕES
# ══════════════════════════════════════════════════════════════════════════
with tab_entry:
    verificar_permissao_modulo("Financeiro - Lançamentos")
    st.subheader("💸 Lançamentos Financeiros")
    
    sub_tab_pedido, sub_tab_avulso = st.tabs(["📋 Vínculo com Pedidos", "💰 Movimentação Avulsa (Fluxo)"])
    
    with sub_tab_pedido:
        st.markdown("### Lançamento de Custos e Recebimentos")
        query = """
            SELECT o.*, c.nome as cliente_nome 
            FROM orcamentos o
            JOIN clientes c ON o.cliente_id = c.id
            WHERE o.status = 'Aprovado'
            ORDER BY o.data DESC
        """
        df_aprov = cached_buscar_dados(query, version=financeiro_cache_version)

        if df_aprov.empty:
            st.info("💡 Nenhum orçamento aprovado para lançamento.")
        else:
            def badge_pag(s):
                if s == "Pago Total":   return '<span class="fin-badge-pago">✅ Pago Total</span>'
                if s == "Parcial":      return '<span class="fin-badge-parcial">🔶 Pago Parcial</span>'
                return '<span class="fin-badge-pend">🔴 Pendente</span>'

            opcoes = []
            for _, r in df_aprov.iterrows():
                s_pag = get_val(r, 'status_pagamento', 'Pendente')
                emoji = "✅" if s_pag == "Pago Total" else ("🟡" if s_pag == "Parcial" else "🔴")
                opcoes.append(f"{emoji} {r['id']} — {r['cliente_nome']} (R$ {r['total']:,.2f})")

            sel = st.selectbox("Selecione o Pedido:", ["— Escolha —"] + opcoes, key="sel_pedido")

            if sel != "— Escolha —":
                id_pedido = sel.split(" ")[1].strip()
                pedido = df_aprov[df_aprov['id'] == id_pedido].iloc[0]

                df_formas = cached_buscar_dados("SELECT nome, taxa FROM formas_pagamento ORDER BY nome", version=financeiro_cache_version)
                formas_map = dict(zip(df_formas['nome'], df_formas['taxa'])) if not df_formas.empty else {}
                formas_nomes = ["-- Selecione --"] + list(formas_map.keys())

                st.divider()

                st.markdown(f"""
                    <div style='background: rgba(15,40,71,0.3); border: 1px solid rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; margin-bottom: 25px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='color:#94a3b8; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:1px;'>GESTÃO FINANCEIRA DO PEDIDO</span>
                                <h2 style='margin:0; color:#f8fafc;'>Ref: {id_pedido} — {pedido['cliente_nome']}</h2>
                            </div>
                            <div style='text-align:right;'>
                                <span style='color:#94a3b8; font-size:0.7rem; font-weight:700;'>STATUS ATUAL</span><br>
                                {badge_pag(get_val(pedido, 'status_pagamento', 'Pendente'))}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_custo, col_pag = st.columns([1.1, 1], gap="large")

                with col_custo:
                    st.markdown("#### 🛠️ Custos de Produção")
                    itens = safe_loads(get_val(pedido, 'itens_json', '[]'))
                    custo_atual = float(get_val(pedido, 'custo_producao', 0))

                    if itens:
                        custos_items = []
                        total_venda = 0
                        for i in itens:
                            try:
                                qtd   = float(i.get('qtd', 1))
                                dim   = i.get('dimensoes', '-')
                                fator = 1.0
                                if 'x' in str(dim):
                                    try:
                                        p = str(dim).split('x')
                                        fator = float(p[0]) * float(p[1])
                                    except: fator = 1.0
                                c_proc = float(i.get('custo_processamento', 0))
                                c_depr = float(i.get('depreciacao', 0))
                                c_ins  = 0
                                try:
                                    comp = json.loads(i.get('composicao_json', '[]') or '[]')
                                    c_ins = sum(float(x.get('Custo (R$)', 0)) for x in comp)
                                except: pass
                                custo_est = float((c_proc + c_depr + c_ins) * qtd * fator)
                            except: custo_est = 0

                            sub = float(i.get('subtotal', 0))
                            total_venda += sub
                            custos_items.append({
                                "Item": i.get('produto') or i.get('item') or "Item",
                                "Venda (R$)": float(sub),
                                "Custo Real (R$)": float(custo_est if custo_atual == 0 else (custo_atual / max(len(itens), 1)))
                            })

                        df_custos = pd.DataFrame(custos_items)
                        with st.container(border=True):
                            new_df = st.data_editor(df_custos, use_container_width=True, hide_index=True, key="editor_custos")
                            total_custo_real = float(new_df["Custo Real (R$)"].sum())
                            total_venda_real = float(new_df["Venda (R$)"].sum())

                        margem = ((total_venda_real - total_custo_real) / total_venda_real * 100) if total_venda_real > 0 else 0
                        lucro_valor = total_venda_real - total_custo_real
                        
                        st.markdown(f"""
                            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-top: 15px;'>
                                <div style='background: rgba(255,255,255,0.03); padding: 15px; border-radius: 12px; border-left: 4px solid #38bdf8;'>
                                    <span style='color:#94a3b8; font-size:0.7rem; font-weight:700;'>TOTAL VENDA</span><br>
                                    <span style='color:#f8fafc; font-size:1.2rem; font-weight:800;'>R$ {total_venda_real:,.2f}</span>
                                </div>
                                <div style='background: rgba(255,255,255,0.03); padding: 15px; border-radius: 12px; border-left: 4px solid #94a3b8;'>
                                    <span style='color:#94a3b8; font-size:0.7rem; font-weight:700;'>CUSTO TOTAL</span><br>
                                    <span style='color:#f1f5f9; font-size:1.2rem; font-weight:800;'>R$ {total_custo_real:,.2f}</span>
                                </div>
                                <div style='background: rgba(34,197,94,0.1); padding: 15px; border-radius: 12px; border-left: 4px solid #22c55e;'>
                                    <span style='color:#22c55e; font-size:0.7rem; font-weight:700;'>MARGEM BRUTA</span><br>
                                    <span style='color:#22c55e; font-size:1.2rem; font-weight:800;'>{margem:.1f}%</span><br>
                                    <small style='color:#4ade80;'>Lucro: R$ {lucro_valor:,.2f}</small>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Itens não encontrados.")
                        total_custo_real = 0

                with col_pag:
                    st.markdown("#### 💳 Recebimento e Taxas")
                    total_pedido = float(get_val(pedido, 'total', 0))

                    with st.container(border=True):
                        st.markdown("<span style='font-size:0.75rem; font-weight:700; color:#94a3b8;'>TAXAS E MEIO DE PAGAMENTO</span>", unsafe_allow_html=True)
                        forma_salva = get_val(pedido, 'forma_pagamento_fin', '-- Selecione --')
                        idx_forma = formas_nomes.index(forma_salva) if forma_salva in formas_nomes else 0
                        sel_forma = st.selectbox("Forma de Pagamento", formas_nomes, index=idx_forma, key="forma_fin", label_visibility="collapsed")

                        taxa_pct = 0.0
                        if sel_forma != "-- Selecione --":
                            taxa_pct = float(formas_map.get(sel_forma, 0))

                        taxa_pct_edit = st.number_input(
                            f"Taxa da Forma %",
                            min_value=0.0, max_value=50.0,
                            value=float(taxa_pct or 0), step=0.01, format="%.2f",
                            help="Ajuste manual da taxa"
                        )
                        valor_taxa  = float(total_pedido * taxa_pct_edit / 100)
                        valor_liq   = float(total_pedido - valor_taxa)

                        st.markdown(f"""
                            <div style="background: rgba(2,6,23,0.4); border-radius:10px; padding:12px; margin:10px 0">
                                <div class="fin-row"><span class="fin-label">Total Pedido</span><span class="fin-value">R$ {total_pedido:,.2f}</span></div>
                                <div class="fin-row"><span class="fin-label">Taxa ({taxa_pct_edit:.2f}%)</span><span class="fin-value" style="color:#f87171">- R$ {valor_taxa:,.2f}</span></div>
                                <div class="fin-row" style="border:none"><span class="fin-label" style="color:#22c55e;font-weight:700;">VALOR LÍQUIDO</span><span class="fin-value" style="color:#22c55e;font-size:1.1rem;">R$ {valor_liq:,.2f}</span></div>
                            </div>
                        """, unsafe_allow_html=True)

                    with st.container(border=True):
                        st.markdown("<span style='font-size:0.75rem; font-weight:700; color:#94a3b8;'>CONTROLE DE FLUXO (CAIXA)</span>", unsafe_allow_html=True)
                        f_col1, f_col2 = st.columns(2)
                        valor_entrada = f_col1.number_input("Valor Entrada (R$)", min_value=0.0, value=float(get_val(pedido, 'valor_entrada', 0)))
                        valor_total_pago = f_col2.number_input("Total Já Pago (R$)", min_value=0.0, value=float(get_val(pedido, 'valor_pago', 0)))

                        saldo_devedor = round(total_pedido - valor_total_pago, 2)
                        
                        st.markdown(f"""
                            <div style="background: rgba(2,6,23,0.4); border-radius:10px; padding:12px; margin:10px 0">
                                <div class="fin-row"><span class="fin-label">Saldo Devedor</span><span class="fin-value" style="color:{'#22c55e' if saldo_devedor<=0 else '#f87171'}">R$ {max(saldo_devedor,0):,.2f}</span></div>
                            </div>
                        """, unsafe_allow_html=True)

                        if valor_total_pago >= total_pedido: status_pag_auto = "Pago Total"
                        elif valor_total_pago > 0: status_pag_auto = "Parcial"
                        else: status_pag_auto = "Pendente"
                        
                        st.markdown(f"**Status:** {badge_pag(status_pag_auto)}", unsafe_allow_html=True)

                    with st.container(border=True):
                        d_col1, d_col2 = st.columns(2)
                        data_pag = d_col1.date_input("📅 Data Pgto", value=datetime.now())
                        with d_col2:
                            with st.popover("📸 Comprovante"):
                                comp_atual = get_val(pedido, 'comprovante_base64', None)
                                if comp_atual:
                                    try: st.image(base64.b64decode(comp_atual), use_container_width=True)
                                    except: pass
                                up_file = st.file_uploader("Novo", type=['png','jpg','jpeg'], key="up_comp_fin")
                        
                        obs_fin = st.text_area("📝 Observações Financeiras", value=str(get_val(pedido, 'financeiro_obs', '') or ''), height=65)

                    if st.button("💾 ATUALIZAR FINANCEIRO", type="primary", use_container_width=True):
                        comp_b64 = comp_atual or ''
                        if up_file: comp_b64 = base64.b64encode(up_file.read()).decode()

                        executar_comando("""
                            UPDATE orcamentos SET
                                custo_producao     = ?,
                                valor_entrada      = ?,
                                valor_pago         = ?,
                                taxa_cartao        = ?,
                                valor_liquido      = ?,
                                status_pagamento   = ?,
                                forma_pagamento_fin = ?,
                                comprovante_base64 = ?,
                                data_pagamento     = ?,
                                financeiro_obs     = ?
                            WHERE id = ?
                        """, (
                            total_custo_real, valor_entrada, valor_total_pago,
                            taxa_pct_edit, valor_liq, status_pag_auto,
                            sel_forma, comp_b64, data_pag.strftime("%Y-%m-%d"),
                            obs_fin, id_pedido
                        ))
                        bump_financeiro_cache_version()
                        bump_orcamentos_cache_version()
                        st.success(f"✅ Pedido {id_pedido} atualizado!")
                        st.rerun()

    with sub_tab_avulso:
        st.subheader("📈 Controle de Movimentações Financeiras")
        st.caption("Registre gastos e entradas avulsas ou vinculadas a pedidos.")

        df_projs_o = cached_buscar_dados("SELECT id, (id || ' - ' || (SELECT nome FROM clientes WHERE id=cliente_id LIMIT 1)) as display FROM orcamentos WHERE status='Aprovado'", version=financeiro_cache_version)
        df_projs_m = cached_buscar_dados("SELECT numero_orcamento as id, (numero_orcamento || ' - ' || cliente) as display FROM projetos", version=financeiro_cache_version)
        
        list_o = df_projs_o['display'].tolist() if not df_projs_o.empty else []
        list_m = df_projs_m['display'].tolist() if not df_projs_m.empty else []
        projs_list = ["-- Sem Vínculo --"] + list_o + list_m
        
        col_add1, col_add2 = st.columns(2)
        
        with col_add1:
            with st.expander("💸 Registrar Novo Gasto (Saída)", expanded=False):
                with st.form("form_gasto"):
                    proj_sel = st.selectbox("Vincular a Pedido:", projs_list)
                    data_g = st.date_input("Data do Gasto", value=datetime.now())
                    desc_g = st.text_input("Descrição do Gasto")
                    cat_g = st.selectbox("Categoria", ["Material", "Mão de Obra", "Transporte", "Ferramentas", "Impostos", "Comissão", "Outros"])
                    val_g = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
                    
                    if st.form_submit_button("✅ Salvar Gasto", use_container_width=True):
                        id_p = proj_sel.split(" - ")[0] if proj_sel != "-- Sem Vínculo --" else None
                        executar_comando("""
                            INSERT INTO gastos (projeto_id, data_gasto, descricao, categoria, valor)
                            VALUES (?, ?, ?, ?, ?)
                        """, (id_p, data_g.strftime("%Y-%m-%d"), desc_g, cat_g, val_g))
                        bump_financeiro_cache_version()
                        st.success("Gasto registrado!")
                        st.rerun()

        with col_add2:
            with st.expander("💰 Registrar Nova Entrada (Recebimento)", expanded=False):
                with st.form("form_entrada"):
                    proj_sel_e = st.selectbox("Vincular a Pedido:", projs_list, key="sel_proj_e")
                    data_e = st.date_input("Data do Recebimento", value=datetime.now())
                    forma_e = st.selectbox("Forma de Pagamento", ["Dinheiro", "PIX", "Cartão", "Boleto", "Transferência"])
                    val_e = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f", key="val_e")
                    
                    if st.form_submit_button("✅ Salvar Entrada", use_container_width=True):
                        id_p_e = proj_sel_e.split(" - ")[0] if proj_sel_e != "-- Sem Vínculo --" else None
                        executar_comando("""
                            INSERT INTO entradas (projeto_id, data_pagamento, valor, forma_pagamento)
                            VALUES (?, ?, ?, ?)
                        """, (id_p_e, data_e.strftime("%Y-%m-%d"), val_e, forma_e))
                        bump_financeiro_cache_version()
                        st.success("Recebimento registrado!")
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# ABA 3 — EXTRATO & RELATÓRIOS
# ══════════════════════════════════════════════════════════════════════════
with tab_records:
    verificar_permissao_modulo("Financeiro - Relatórios")
    sub_rep_extrato, sub_rep_pdf, sub_rep_html = st.tabs(["📊 Extrato Geral", "📄 Relatório PDF", "✨ Comprovante HTML"])
    
    with sub_rep_extrato:
        st.subheader("📈 Consulta de Registros")
        q_res = """
            SELECT o.id, c.nome as cliente, o.total as faturamento,
                   o.custo_producao, o.valor_entrada, o.valor_pago,
                   o.taxa_cartao, o.valor_liquido,
                   o.status_pagamento, o.forma_pagamento_fin, o.data_pagamento
            FROM orcamentos o
            JOIN clientes c ON o.cliente_id = c.id
            WHERE o.status = 'Aprovado'
            ORDER BY o.data DESC
        """
        df_res = cached_buscar_dados(q_res, version=financeiro_cache_version).fillna(0)

        if df_res.empty:
            st.info("Nenhum pedido aprovado para exibir.")
        else:
            df_res['lucro']        = df_res['faturamento'] - df_res['custo_producao']
            df_res['saldo_dev']    = df_res['faturamento'] - df_res['valor_pago']
            df_res['saldo_dev']    = df_res['saldo_dev'].clip(lower=0)

            filt_status = st.multiselect(
                "Filtrar por Status de Pagamento:",
                options=["Pendente","Parcial","Pago Total"],
                default=["Pendente","Parcial","Pago Total"],
                key="filt_status_extrato"
            )
            df_filt = df_res[df_res['status_pagamento'].isin(filt_status)] if filt_status else df_res

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Faturamento",         f"R$ {df_filt['faturamento'].sum():,.2f}")
            m2.metric("Total Recebido",      f"R$ {df_filt['valor_pago'].sum():,.2f}")
            m3.metric("Saldo a Receber",     f"R$ {df_filt['saldo_dev'].sum():,.2f}")
            m4.metric("Lucro Líq. (Custos)", f"R$ {df_filt['lucro'].sum():,.2f}")
            m5.metric("Taxas Perdidas",      f"R$ {(df_filt['faturamento'] * df_filt['taxa_cartao'] / 100).sum():,.2f}")

            st.divider()

            def color_st(val):
                if val == "Pago Total": return "color: #22c55e; font-weight:bold"
                if val == "Parcial":    return "color: #fbbf24; font-weight:bold"
                return "color: #f87171"

            df_view = df_filt[['id','cliente','faturamento','valor_entrada','valor_pago','taxa_cartao','valor_liquido','lucro','saldo_dev','status_pagamento','forma_pagamento_fin']].copy()
            df_view.columns = ['ID','Cliente','Faturamento','Entrada','Total Pago','Taxa %','Liq. (s/ taxa)','Lucro','Saldo Dev.','Status','Forma Pag.']

            st.dataframe(
                df_view.style
                    .format({
                        "Faturamento": "R$ {:,.2f}", "Entrada": "R$ {:,.2f}",
                        "Total Pago": "R$ {:,.2f}",  "Liq. (s/ taxa)": "R$ {:,.2f}",
                        "Lucro": "R$ {:,.2f}",        "Saldo Dev.": "R$ {:,.2f}",
                        "Taxa %": "{:.2f}%"
                    })
                    .map(color_st, subset=["Status"]),
                use_container_width=True,
                hide_index=True
            )

    with sub_rep_pdf:
        st.subheader("📄 Gerador de Relatório PDF Profissional")
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            filt_rpt = st.selectbox("Filtrar por Status no Relatório:", ["Todos", "Pendente", "Parcial", "Pago Total"], key="filtro_status_pdf")
        with col_opt2:
            tit_rel = st.text_input("Título do Relatório:", value="Relatório Financeiro Geral")

        q_pdf = """
            SELECT o.id, c.nome as cliente, o.total as faturamento,
                   o.custo_producao, o.valor_entrada, o.valor_pago,
                   o.taxa_cartao, o.valor_liquido,
                   o.status_pagamento, o.forma_pagamento_fin
            FROM orcamentos o
            JOIN clientes c ON o.cliente_id = c.id
            WHERE o.status = 'Aprovado'
            ORDER BY o.data DESC
        """
        df_pdf = cached_buscar_dados(q_pdf, version=financeiro_cache_version).fillna(0)
        if filt_rpt != "Todos":
            df_pdf = df_pdf[df_pdf['status_pagamento'] == filt_rpt]

        if not df_pdf.empty:
            def gerar_pdf_local(df, titulo):
                pdf = FPDF(orientation='L')
                pdf.add_page()
                pdf.set_font("Courier", "B", 14)
                pdf.cell(0, 10, titulo, ln=True, align="C")
                pdf.set_font("Courier", "", 9)
                pdf.cell(0, 8, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} | {empresa_nome}", ln=True, align="C")
                pdf.ln(6)
                cols_pdf = [
                    ("ID", 22), ("Cliente", 55), ("Venda", 25),
                    ("Entrada", 22), ("Pago", 22), ("Taxa", 15),
                    ("Liq.", 22), ("Custo", 22), ("Lucro", 22),
                    ("Saldo", 22), ("Status", 22),
                ]
                pdf.set_font("Courier", "B", 8)
                pdf.set_fill_color(15, 23, 42)
                pdf.set_text_color(255, 255, 255)
                for col_name, w in cols_pdf:
                    pdf.cell(w, 7, col_name, border=1, align="C", fill=True)
                pdf.ln()
                pdf.set_font("Courier", "", 8)
                pdf.set_text_color(0, 0, 0)
                for _, r in df.iterrows():
                    luc = float(r['faturamento']) - float(r['custo_producao'])
                    sal = max(float(r['faturamento']) - float(r['valor_pago']), 0)
                    lv = float(r['valor_liquido']) if float(r['valor_liquido']) > 0 else float(r['faturamento']) * (1 - float(r['taxa_cartao'])/100)
                    vs = [
                        str(r['id'])[:12], str(r['cliente'])[:30], 
                        f"{float(r['faturamento']):.2f}", f"{float(r['valor_entrada']):.2f}", f"{float(r['valor_pago']):.2f}", 
                        f"{float(r['taxa_cartao']):.1f}%", f"{lv:.2f}", f"{float(r['custo_producao']):.2f}", 
                        f"{luc:.2f}", f"{sal:.2f}", str(r['status_pagamento'] or '—')[:12]
                    ]
                    for idx, v in enumerate(vs):
                        w = cols_pdf[idx][1]
                        align = "R" if (idx > 1 and idx < 10) else "L"
                        pdf.cell(w, 6, v, border=1, align=align)
                    pdf.ln()
                pdf.ln(6)
                pdf.set_font("Courier", "B", 9)
                pdf.set_fill_color(30, 41, 59)
                pdf.set_text_color(255, 255, 255)
                fatur_t = df['faturamento'].sum()
                receb_t = df['valor_pago'].sum()
                saldo_t = (df['faturamento'] - df['valor_pago']).clip(0).sum()
                lucro_t = (df['faturamento'] - df['custo_producao']).sum()
                s_labels = [("Faturamento Total:", fatur_t), ("Total Recebido:", receb_t), ("Saldo a Receber:", saldo_t), ("Lucro Estimado:", lucro_t)]
                for lbl, v in s_labels:
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(60, 8, lbl, border=0, fill=True, align="R")
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(40, 8, f" R$ {v:,.2f}", border=0, fill=False, align="L")
                    pdf.ln()
                return pdf.output(dest="S")

            if st.button("🚀 Gerar PDF Agora", type="primary", use_container_width=True):
                raw_pdf = gerar_pdf_local(df_pdf, tit_rel)
                pdf_bytes = raw_pdf.encode('latin-1') if isinstance(raw_pdf, str) else bytes(raw_pdf)
                st.download_button(label="📥 Baixar Relatório PDF", data=pdf_bytes, file_name=f"Relatorio_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf", use_container_width=True)

    with sub_rep_html:
        st.subheader("✨ Gerador de Comprovante Premium")
        q_html = "SELECT o.id, c.nome as cliente, o.total, o.valor_entrada, o.valor_pago, o.taxa_cartao, o.valor_liquido, o.status_pagamento, o.forma_pagamento_fin, o.data_pagamento FROM orcamentos o JOIN clientes c ON o.cliente_id = c.id WHERE o.status = 'Aprovado' ORDER BY o.data DESC"
        df_html = cached_buscar_dados(q_html, version=financeiro_cache_version)
        if not df_html.empty:
            p_list = [f"{r['id']} - {r['cliente']} (R$ {r['total']:,.2f})" for _, r in df_html.iterrows()]
            p_sel = st.selectbox("Selecione o Pedido:", p_list, key="sel_html_receipt")
            if p_sel:
                hid = p_sel.split(" - ")[0]
                rh = df_html[df_html['id'] == hid].iloc[0]
                v_tabs = {
                    "STATUS_PAGAMENTO": str(rh['status_pagamento']).upper(), "CLIENTE_NOME": rh['cliente'], "ID_PEDIDO": rh['id'], "DATA_EMISSAO": datetime.now().strftime("%d/%m/%Y"),
                    "FORMA_PAGAMENTO": rh['forma_pagamento_fin'] or "A combinar", "VALOR_BRUTO": f"{float(rh['total']):,.2f}", "VALOR_TAXAS": f"{float(rh['total'] - rh['valor_liquido']):,.2f}",
                    "VALOR_TOTAL": f"{float(rh['valor_liquido']):,.2f}", "CHAVE_ACESSO": f"JUV-{rh['id']}-{datetime.now().strftime('%Y%j')}", "TIMESTAMP_GERACAO": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "ITEM_NOME": "Serviços de Serralheria e Vidraçaria", "ITEM_QTD": "1", "ITEM_VALOR_UNIT": f"{float(rh['total']):,.2f}", "ITEM_SUBTOTAL": f"{float(rh['total']):,.2f}"
                }
                h_render = renderizar_template("comprovante_premium.html", v_tabs)
                st.components.v1.html(h_render, height=700, scrolling=True)
                st.download_button("📥 Baixar Comprovante Digital", data=h_render, file_name=f"Comprovante_{str(rh['cliente']).replace(' ', '_')}_{hid}.html", mime="text/html", use_container_width=True)

    st.divider()

    q_gastos = """
        SELECT g.id, g.data_gasto as data, 'Saída' as tipo, 
               COALESCE(c.nome, 'Geral') as projeto,
               (g.categoria || ': ' || g.descricao) as descricao,
               (-1 * g.valor) as valor
        FROM gastos g
        LEFT JOIN orcamentos o ON g.projeto_id = o.id
        LEFT JOIN clientes c ON o.cliente_id = c.id
    """
    q_entradas = """
        SELECT e.id, e.data_pagamento as data, 'Entrada' as tipo,
               COALESCE(c.nome, 'Geral') as projeto,
               ('Pagamento: ' || e.forma_pagamento) as descricao,
               e.valor as valor
        FROM entradas e
        LEFT JOIN orcamentos o ON e.projeto_id = o.id
        LEFT JOIN clientes c ON o.cliente_id = c.id
    """
    df_g = cached_buscar_dados(q_gastos, version=financeiro_cache_version)
    df_ent = cached_buscar_dados(q_entradas, version=financeiro_cache_version)
    df_fluxo_total = pd.concat([df_g, df_ent]).sort_values(by='data', ascending=False)
    
    if not df_fluxo_total.empty:
        t_ent = df_ent['valor'].sum() if not df_ent.empty else 0
        t_sai = abs(df_g['valor'].sum()) if not df_g.empty else 0
        saldo = t_ent - t_sai
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Entradas", f"R$ {t_ent:,.2f}")
        c2.metric("Total Saídas", f"R$ {t_sai:,.2f}", delta_color="inverse")
        c3.metric("Saldo Geral", f"R$ {saldo:,.2f}", delta=f"R$ {saldo:,.2f}")

        def style_fluxo(row):
            color = "#22c55e" if row['tipo'] == 'Entrada' else "#f87171"
            return [f'color: {color}'] * len(row)

        st.dataframe(df_fluxo_total.style.apply(style_fluxo, axis=1).format({"valor": "R$ {:,.2f}"}), use_container_width=True, hide_index=True)

        with st.expander("🗑️ Excluir Movimentação"):
            col_ex1, col_ex2 = st.columns([3, 1])
            opcoes_ex = [f"{r['tipo']} - {r['data']} - {r['descricao']} (R$ {r['valor']:,.2f}) [ID:{r['id']}]" for _, r in df_fluxo_total.iterrows()]
            sel_ex = col_ex1.selectbox("Selecione a movimentação para excluir:", opcoes_ex)
            if col_ex2.button("🚫 EXCLUIR", type="primary", use_container_width=True):
                parts = sel_ex.split("[ID:")
                if len(parts) > 1:
                    tipo_ex = sel_ex.split(" - ")[0]
                    id_ex = parts[1].split("]")[0]
                    tabela_ex = "gastos" if tipo_ex == "Saída" else "entradas"
                    executar_comando(f"DELETE FROM {tabela_ex} WHERE id = ?", (id_ex,))
                    bump_financeiro_cache_version()
                    st.rerun()

        st.divider()
        if st.button("📊 Exportar Fluxo de Caixa para Excel"):
            try:
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_fluxo_total.to_excel(writer, sheet_name='Fluxo_de_Caixa', index=False)
                    df_g.to_excel(writer, sheet_name='Gastos_Detalhados', index=False)
                    df_ent.to_excel(writer, sheet_name='Entradas_Detalhadas', index=False)
                st.download_button(label="📥 Clique aqui para Baixar Excel", data=output.getvalue(), file_name=f"Fluxo_Caixa_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao exportar Excel: {e}")

# ══════════════════════════════════════════════════════════════════════════
# ABA 4 — GESTÃO DE PROJETOS & DADOS
# ══════════════════════════════════════════════════════════════════════════
with tab_manage:
    manage_sub1, manage_sub2 = st.tabs(["📂 Projetos Manuais", "🔗 Integração Externa"])
    
    with manage_sub1:
        st.subheader("📂 Gerenciamento de Projetos ERP")
        st.caption("Cadastre projetos manuais ou visualize orçamentos vinculados.")

        with st.expander("➕ Novo Projeto Manual", expanded=False):
            with st.form("form_novo_projeto"):
                auto_num = datetime.now().strftime("MAN-%Y%m%d%H%M%S")
                c1, c2 = st.columns(2)
                num_p = c1.text_input("Número do Projeto/Referência", value=auto_num)
                cli_p = c2.text_input("Nome do Cliente")
                c3, c4, c5 = st.columns(3)
                data_o = c3.date_input("Data Orçamento", value=datetime.now())
                data_a = c4.date_input("Data Aprovação", value=datetime.now())
                val_v  = c5.number_input("Valor de Venda (R$)", min_value=0.0, step=0.01)
                desc_p = st.text_area("Descrição/Detalhes")
                
                if st.form_submit_button("✅ Cadastrar Projeto"):
                    try:
                        executar_comando("INSERT INTO projetos (numero_orcamento, cliente, data_orcamento, data_aprovacao, descricao, valor_venda, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (num_p, cli_p, data_o.strftime("%Y-%m-%d"), data_a.strftime("%Y-%m-%d"), desc_p, val_v, 'Aprovado'))
                        bump_financeiro_cache_version()
                        st.success("Projeto cadastrado!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error(f"❌ Erro: O ID '{num_p}' já existe.")
                    except Exception as e:
                        st.error(f"❌ Erro ao cadastrar: {e}")

        st.divider()
        query_p = "SELECT * FROM projetos ORDER BY data_orcamento DESC"
        df_projs_man = cached_buscar_dados(query_p, version=financeiro_cache_version)
        if not df_projs_man.empty:
            st.write("### Projetos Cadastrados")
            for _, row in df_projs_man.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:15px; margin-bottom:10px">
                        <div style="display:flex; justify-content:space-between; align-items:center">
                            <span style="font-weight:800; color:#38bdf8; font-size:1.1rem">{row['numero_orcamento']}</span>
                            <span style="background:rgba(56,189,248,0.1); color:#38bdf8; padding:2px 8px; border-radius:5px; font-size:0.8rem">ID: {row['id']}</span>
                        </div>
                        <div style="margin-top:8px"><strong>Cliente:</strong> {row['cliente']}</div>
                        <div style="margin-top:4px; font-size:0.9rem; color:#94a3b8"><strong>Valor:</strong> R$ {row['valor_venda']:,.2f} | <strong>Data:</strong> {row['data_orcamento']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    c_del, c_view = st.columns([1, 4])
                    if c_del.button("🗑️", key=f"del_p_{row['id']}"):
                        executar_comando("DELETE FROM projetos WHERE id = ?", (row['id'],))
                        bump_financeiro_cache_version()
                        st.rerun()
        else:
            st.info("Nenhum projeto manual cadastrado.")

    with manage_sub2:
        st.subheader("🔗 Integração com Bancos Externos")
        st.caption("Conecte bases SQLite de outros sistemas para importar lançamentos.")
        favs = cached_buscar_dados("SELECT * FROM diretorios_favoritos", version=financeiro_cache_version)
        with st.expander("⚙️ Configurar Diretórios Favoritos", expanded=False):
            c_path, c_add = st.columns([3, 1])
            new_path = c_path.text_input("Caminho do Diretório (Ex: C:\\MeusBancos)", key="new_dir_path")
            if c_add.button("⭐ Adicionar", use_container_width=True):
                if os.path.exists(new_path):
                    exists = buscar_dados("SELECT 1 FROM diretorios_favoritos WHERE caminho = ?", (new_path,))
                    if exists.empty:
                        executar_comando("INSERT INTO diretorios_favoritos (caminho, nome) VALUES (?, ?)", (new_path, os.path.basename(new_path)))
                        bump_financeiro_cache_version()
                        st.success("Caminho salvo!")
                        st.rerun()
                    else:
                        st.info("Este diretório já está nos favoritos.")
                else: 
                    st.error("Caminho não existe.")

            if not favs.empty:
                for _, f in favs.iterrows():
                    col_f1, col_f2 = st.columns([4, 1])
                    col_f1.code(f['caminho'])
                    if col_f2.button("❌", key=f"del_fav_{f['id']}"):
                        executar_comando("DELETE FROM diretorios_favoritos WHERE id = ?", (f['id'],))
                        bump_financeiro_cache_version()
                        st.rerun()

        diretorios = ["Selecione..."] + favs['caminho'].tolist() if not favs.empty else ["Selecione..."]
        sel_dir = st.selectbox("Selecione o diretório para escanear:", diretorios)
        if sel_dir != "Selecione...":
            import sqlite3
            dbs = [f for f in os.listdir(sel_dir) if f.endswith('.db') or f.endswith('.sqlite')]
            if dbs:
                db_file = st.selectbox("Selecione o arquivo do Banco de Dados:", dbs)
                db_path = os.path.join(sel_dir, db_file)
                try:
                    conn_ext = sqlite3.connect(db_path)
                    tabs_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn_ext)
                    table_name = st.selectbox("Selecione a Tabela:", tabs_df['name'].tolist())
                    if table_name:
                        df_ext = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 50", conn_ext)
                        st.dataframe(df_ext, use_container_width=True)
                    conn_ext.close()
                except Exception as e:
                    st.error(f"Erro ao ler banco externo: {e}")

    st.divider()
