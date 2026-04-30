import streamlit as st
import os
import sys

if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import json
import base64
from datetime import datetime
from database import buscar_dados, executar_comando
from TEMAS.moderno import apply_modern_style
from utils.auth_manager import verificar_autenticacao, obter_dados_empresa, verificar_permissao_modulo
from utils.documentos import GeradorPDF
from utils.query_cache import cached_buscar_dados, get_clientes_cache_version, bump_orcamentos_cache_version

def safe_loads(json_str):
    try:
        return json.loads(json_str) if json_str else []
    except:
        return []

# --- CONFIGURAÇÃO DA PÁGINA ---
clientes_cache_version = get_clientes_cache_version()
df_conf = cached_buscar_dados("SELECT * FROM config LIMIT 1", version=clientes_cache_version)
nome_empresa = df_conf.iloc[0]['empresa_nome'] if not df_conf.empty else "Sistema"
st.set_page_config(page_title=f"Novo Orçamento | {nome_empresa}", layout="wide", page_icon="📝")

_, logo_src = obter_dados_empresa()
apply_modern_style(logo_url=logo_src)

verificar_autenticacao()
from utils.auth_manager import verificar_nivel_acesso
verificar_nivel_acesso(["ADMIN", "GERENTE", "VENDEDOR"])
verificar_permissao_modulo("Orçamentos")

# --- INICIALIZAÇÃO DE ESTADO ---
if 'id_orc_atual' not in st.session_state:
    st.session_state.id_orc_atual = f"ORC-{datetime.now().strftime('%y%m%d%H%M')}"
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- CABEÇALHO ---
st.title("📝 Engenharia de Orçamentos")
st.markdown(f"**Referência:** `{st.session_state.id_orc_atual}`")

# ═══════════════════════════════════════════════
# PASSO 1: CLIENTE E VENDEDOR
# ═══════════════════════════════════════════════
st.markdown("### 👤 PASSO 1: Identificação")
with st.container(border=True):
    c1, c2 = st.columns([1, 1])
    df_clientes = cached_buscar_dados("SELECT id, nome, cnpj, telefone, endereco, numero FROM clientes", version=clientes_cache_version)
    
    termo_busca = c1.text_input("🔍 Localizar Cliente (Nome ou CNPJ)", placeholder="Pesquisar...", key="busca_cliente_orc")
    cliente_selecionado = None
    
    if termo_busca:
        mask = df_clientes.apply(lambda r: r.astype(str).str.contains(termo_busca, case=False).any(), axis=1)
        df_filtrado = df_clientes[mask]
        if not df_filtrado.empty:
            cliente_selecionado = c2.selectbox("Selecione:", options=df_filtrado.to_dict('records'), format_func=lambda x: f"👤 {x['nome']}", key="sel_cliente_orc")
        else:
            c2.warning("Nenhum cliente encontrado.")
    
    cv1, cv2, cv3 = st.columns(3)
    df_vds = cached_buscar_dados("SELECT nome FROM vendedores ORDER BY nome", version=clientes_cache_version)
    lista_vds = df_vds['nome'].tolist() if not df_vds.empty else ["Admin"]
    vendedor_atual = cv1.selectbox("Vendedor", options=lista_vds, key="sel_vendedor_orc")
    validade_dias = cv2.number_input("Validade (Dias)", min_value=1, value=3, key="validade_orc")
    prazo_entrega = cv3.text_input("Prazo de Entrega", value="20 dias úteis", key="prazo_orc")

# ═══════════════════════════════════════════════
# PASSO 2: ADICIONAR ITENS
# ═══════════════════════════════════════════════
st.markdown("### 📦 PASSO 2: Itens do Orçamento")
tab1, tab2 = st.tabs(["📁 Catálogo de Produtos", "✨ Item Personalizado / Serviço"])

with tab1:
    with st.container(border=True):
        cp1, cp2 = st.columns([1, 1])
        busca_p = cp1.text_input("Buscar no Catálogo", placeholder="Digite o nome do produto...", key="busca_prod_cat")
        df_p = cached_buscar_dados("SELECT * FROM produtos", version=clientes_cache_version)
        if busca_p:
            df_pf = df_p[df_p.apply(lambda r: r.astype(str).str.contains(busca_p, case=False).any(), axis=1)]
            if not df_pf.empty:
                p_obj = cp2.selectbox("Produto:", df_pf.to_dict('records'), format_func=lambda x: f"{x['nome']} - R$ {x['preco']:.2f}/{x['unidade']}", key="sel_prod_cat")
                st.divider()
                p1, p2, p3, p4 = st.columns(4)
                qtd = p1.number_input("Quantidade", min_value=1, value=1, key="qtd_cat")
                unidade = p_obj['unidade']
                is_m2 = "m2" in str(unidade).lower() or "m²" in str(unidade).lower()
                alt = p2.number_input("Altura (m)", value=1.0, disabled=not is_m2, key="alt_cat")
                lar = p3.number_input("Largura (m)", value=1.0, disabled=not is_m2, key="lar_cat")
                
                fator = (alt * lar) if is_m2 else 1.0
                subtotal = round(float(p_obj['preco']) * qtd * fator, 2)
                
                obs_item = st.text_input("Observação deste item", key="obs_item_cat")
                if st.button("🚀 Adicionar ao Orçamento", use_container_width=True, type="primary", key="btn_add_cat"):
                    st.session_state.carrinho.append({
                        "tipo": "Catálogo", "produto": p_obj['nome'], "qtd": qtd, "unidade": unidade,
                        "dimensoes": f"{alt:.2f}x{lar:.2f}" if is_m2 else "-", "preco_un": float(p_obj['preco']),
                        "subtotal": subtotal, "descricao": obs_item
                    })
                    st.rerun()

with tab2:
    with st.container(border=True):
        n_c = st.text_input("Nome do Item ou Serviço", placeholder="Ex: Manutenção Elétrica...", key="nome_item_pers")
        tp1, tp2, tp3 = st.columns(3)
        u_c = tp1.selectbox("Tipo de Cobrança", ["un", "m2", "hora", "serviço", "kg", "m"], key="tipo_cobr_pers")
        
        is_m2_c = u_c == "m2"
        is_hora = u_c == "hora"
        
        if is_hora:
            p_c = tp2.number_input("Valor da Hora (R$)", min_value=0.0, value=0.0, step=1.0, format="%.2f", key="preco_hora_pers")
            q_c = tp3.number_input("Total de Horas", min_value=1, value=1, key="qtd_hora_pers")
            n_pessoas = st.number_input("Nº de Profissionais", min_value=1, value=1, key="pessoas_hora_pers")
            fator_c = n_pessoas
            dim_txt = f"{q_c}h x {n_pessoas}p"
        elif is_m2_c:
            p_c = tp2.number_input("Preço por m² (R$)", min_value=0.0, value=0.0, step=1.0, format="%.2f", key="preco_m2_pers")
            q_c = tp3.number_input("Quantidade de Peças", min_value=1, value=1, key="qtd_m2_pers")
            m1, m2 = st.columns(2)
            alt_c = m1.number_input("Altura (m) ", value=1.0, key="alt_m2_pers")
            lar_c = m2.number_input("Largura (m) ", value=1.0, key="lar_m2_pers")
            fator_c = (alt_c * lar_c)
            dim_txt = f"{alt_c:.2f}x{lar_c:.2f}"
        else:
            p_c = tp2.number_input("Preço Unitário (R$)", min_value=0.0, value=0.0, step=1.0, format="%.2f", key="preco_un_pers")
            q_c = tp3.number_input("Quantidade", min_value=1, value=1, key="qtd_un_pers")
            fator_c = 1.0
            dim_txt = "-"
        
        o_c = st.text_area("Descrição / Detalhes", key="desc_item_pers")
        sub_c = round(p_c * q_c * fator_c, 2)
        
        st.info(f"Subtotal: R$ {sub_c:,.2f}")
        
        if st.button("✨ Adicionar Item Personalizado", use_container_width=True, key="btn_add_pers"):
            if n_c:
                st.session_state.carrinho.append({
                    "tipo": "Personalizado", "produto": n_c, "qtd": q_c, "unidade": u_c,
                    "dimensoes": dim_txt, "preco_un": p_c,
                    "subtotal": sub_c, "descricao": o_c
                })
                st.rerun()

# ═══════════════════════════════════════════════
# PASSO 3: REVISÃO DO CARRINHO
# ═══════════════════════════════════════════════
if st.session_state.carrinho:
    st.markdown("### 🛒 PASSO 3: Revisão dos Itens")
    
    df_car = pd.DataFrame(st.session_state.carrinho)
    df_ed = st.data_editor(
        df_car,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "subtotal": st.column_config.NumberColumn("Total (R$)", disabled=True, format="R$ %.2f"),
            "produto": st.column_config.TextColumn("Item / Produto"),
            "qtd": st.column_config.NumberColumn("Qtd", min_value=1),
            "preco_un": st.column_config.NumberColumn("Unitário", format="R$ %.2f"),
            "unidade": st.column_config.SelectboxColumn("Unidade", options=["un", "m2", "hora", "serviço", "kg", "m"]),
            "tipo": None, "dimensoes": st.column_config.TextColumn("Medidas", disabled=True)
        },
        key="editor_orcamento_v10"
    )
    
    new_carrinho = df_ed.to_dict('records')
    for item in new_carrinho:
        item['subtotal'] = float(item['qtd']) * float(item['preco_un'])
    st.session_state.carrinho = new_carrinho
    
    total_bruto = sum(float(i['subtotal']) for i in st.session_state.carrinho)

    # ═══════════════════════════════════════════════
    # ═══════════════════════════════════════════════
    # PASSO 4: FINALIZAÇÃO E REGRAS FINANCEIRAS
    # ═══════════════════════════════════════════════
    st.markdown("### 💳 PASSO 4: Pagamento e Fechamento")
    with st.container(border=True):
        f1, f2 = st.columns(2)
        with f1:
            df_pag = cached_buscar_dados("SELECT * FROM formas_pagamento", version=clientes_cache_version)
            formas_list = df_pag.to_dict('records') if not df_pag.empty else []
            sel_pag = st.multiselect("Formas de Pagamento:", options=formas_list, format_func=lambda x: f"{x['nome']} ({x['taxa']}%)", key="pagto_orc_final")
            
            # Calcula a maior taxa entre as selecionadas
            taxa_fin = max([float(f['taxa']) for f in sel_pag]) if sel_pag else 0.0
            
            desconto_pct = st.number_input("Desconto Global (%)", min_value=0.0, max_value=100.0, value=0.0, key="desc_orc_final")
            
        with f2:
            obs_geral = st.text_area("Observações Internas", placeholder="Ex: 50% entrada...", key="obs_orc_final")

        valor_com_taxa = total_bruto * (1 + taxa_fin/100)
        total_com_desconto = round(valor_com_taxa * (1 - desconto_pct/100), 2)
        
        st.divider()
        tr1, tr2, tr3 = st.columns(3)
        tr1.metric("Subtotal Itens", f"R$ {total_bruto:,.2f}")
        tr2.metric("Ajuste Financ. (Taxas)", f"{taxa_fin}%", delta=f"R$ {valor_com_taxa - total_bruto:,.2f}")
        tr3.metric("Total do Orçamento", f"R$ {total_com_desconto:,.2f}", delta=f"-{desconto_pct}%" if desconto_pct > 0 else None)

        if st.button("💾 SALVAR E GERAR PDF", type="primary", use_container_width=True, key="btn_salvar_orc_final"):
            if not cliente_selecionado:
                st.error("Selecione um cliente.")
            elif not sel_pag:
                st.error("Selecione a forma de pagamento.")
            else:
                emp_d = df_conf.iloc[0].to_dict() if not df_conf.empty else {}
                forma_txt = ", ".join([f['nome'] for f in sel_pag])
                # Salva as regras selecionadas em JSON para preservar a ordem e os valores exatos no futuro
                regras_json = json.dumps(sel_pag)
                
                pdf_bytes = GeradorPDF.criar_pdf(
                    st.session_state.id_orc_atual, emp_d, cliente_selecionado,
                    st.session_state.carrinho,
                    {
                        "total": total_com_desconto, "forma": forma_txt,
                        "data": datetime.now().strftime("%Y-%m-%d"),
                        "desconto_global": desconto_pct, "prazo_entrega": prazo_entrega,
                        "regras_completas": sel_pag  # Usa apenas as selecionadas na ordem correta
                    },
                    vendedor_atual, validade_dias, obs_geral, prazo_entrega, estilo='futurista'
                )
                
                sql = """
                    INSERT INTO orcamentos (id, cliente_id, itens_json, total, forma_pagamento, data, validade_dias, vendedor, prazo_entrega, status, obs_geral, desconto_global)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (id) DO UPDATE SET
                        cliente_id=EXCLUDED.cliente_id, itens_json=EXCLUDED.itens_json, total=EXCLUDED.total,
                        forma_pagamento=EXCLUDED.forma_pagamento, data=EXCLUDED.data, vendedor=EXCLUDED.vendedor,
                        prazo_entrega=EXCLUDED.prazo_entrega, obs_geral=EXCLUDED.obs_geral, desconto_global=EXCLUDED.desconto_global
                """
                executar_comando(sql, (
                    st.session_state.id_orc_atual, cliente_selecionado['id'], json.dumps(st.session_state.carrinho),
                    total_com_desconto, regras_json, datetime.now().strftime("%Y-%m-%d"),
                    validade_dias, vendedor_atual, prazo_entrega, "Pendente", obs_geral, desconto_pct
                ))
                bump_orcamentos_cache_version()
                
                st.success(f"✅ Orçamento {st.session_state.id_orc_atual} salvo!")
                nome_cli_limpo = str(cliente_selecionado['nome']).replace(' ', '_')
                nome_arquivo_orc = f"Orcamento_{nome_cli_limpo}_{st.session_state.id_orc_atual}.pdf"
                st.download_button("📥 BAIXAR PDF", pdf_bytes, nome_arquivo_orc, "application/pdf", use_container_width=True, key="btn_download_orc_final")
                
                if st.button("✨ NOVO ORÇAMENTO", key="btn_novo_orc_final"):
                    st.session_state.carrinho = []
                    st.session_state.id_orc_atual = f"ORC-{datetime.now().strftime('%y%m%d%H%M')}"
                    st.rerun()
else:
    st.info("🛒 O carrinho está vazio.")