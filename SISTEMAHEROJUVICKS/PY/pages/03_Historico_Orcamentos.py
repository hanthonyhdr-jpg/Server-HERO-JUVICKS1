import streamlit as st
import os, sys, json, base64, requests
from datetime import datetime

if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import buscar_dados, executar_comando, _log as db_log
from utils.documentos import GeradorPDF
from utils.agenda_fotos import limpar_fotos_orcamento
from utils.query_cache import cached_buscar_dados, get_orcamentos_cache_version, bump_orcamentos_cache_version
from TEMAS.moderno import apply_modern_style
from utils.auth_manager import verificar_autenticacao, obter_dados_empresa

def safe_loads(v):
    try:
        return json.loads(v) if v else []
    except (TypeError, json.JSONDecodeError):
        return []


def log_ui_error(contexto, erro):
    db_log(f"[HISTORICO] {contexto}: {erro}")


def resolver_pagamento(forma_pagamento, lista_regras):
    try:
        regras_pdf = json.loads(forma_pagamento) if (forma_pagamento and str(forma_pagamento).startswith('[')) else lista_regras
        forma_txt = ", ".join(regra.get('nome', '') for regra in regras_pdf) if isinstance(regras_pdf, list) else str(forma_pagamento)
    except (TypeError, json.JSONDecodeError):
        regras_pdf, forma_txt = lista_regras, str(forma_pagamento or '')
    return regras_pdf, forma_txt


def obter_cache_key_orcamento(row, cliente):
    payload = {
        "id": row.get('id'),
        "cliente": cliente.get('nome', ''),
        "telefone": cliente.get('telefone', ''),
        "cnpj": cliente.get('cnpj', ''),
        "itens_json": row.get('itens_json', ''),
        "forma_pagamento": row.get('forma_pagamento', ''),
        "total": row.get('total', 0),
        "vendedor": row.get('vendedor', ''),
        "validade_dias": row.get('validade_dias', ''),
        "obs_geral": row.get('obs_geral', ''),
    }
    return json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)


def obter_pdf_orcamento(row, cliente, empresa, lista_regras):
    sid = str(row['id'])
    cache = st.session_state.setdefault("orc_pdf_cache", {})
    cache_key = obter_cache_key_orcamento(row, cliente)
    cache_entry = cache.get(sid)
    if cache_entry and cache_entry.get("cache_key") == cache_key:
        return cache_entry["pdf_bytes"]

    regras_pdf, forma_txt = resolver_pagamento(row.get('forma_pagamento', ''), lista_regras)
    pdf_bytes = GeradorPDF.criar_pdf(
        row['id'], empresa, cliente, safe_loads(row['itens_json']),
        {
            "total": row['total'], 
            "forma": forma_txt, 
            "regras_completas": regras_pdf,
            "desconto_global": row.get('desconto_global', 0)
        },
        row['vendedor'], row['validade_dias'], row.get('obs_geral', ''),
        prazo_entrega=row.get('prazo_entrega', '')
    )
    cache[sid] = {
        "cache_key": cache_key,
        "pdf_bytes": pdf_bytes,
        "file_name": f"Orc_{cliente.get('nome', 'Cliente').replace(' ', '_')}_{row['id']}.pdf"
    }
    return pdf_bytes


def get_pdf_cache(row, cliente):
    sid = str(row['id'])
    cache = st.session_state.get("orc_pdf_cache", {})
    cache_entry = cache.get(sid)
    if not cache_entry:
        return None
    if cache_entry.get("cache_key") != obter_cache_key_orcamento(row, cliente):
        cache.pop(sid, None)
        return None
    return cache_entry

# ── CONFIGURAÇÃO ─────────────────────────────────────────────────────────────
df_conf = buscar_dados("SELECT * FROM config LIMIT 1")
nome_emp = df_conf.iloc[0]['empresa_nome'] if not df_conf.empty else "Sistema"
st.set_page_config(page_title=f"Histórico · {nome_emp}", layout="wide")

_, logo_src = obter_dados_empresa()
apply_modern_style(logo_url=logo_src, nome_empresa=nome_emp)
verificar_autenticacao()
orcamentos_cache_version = get_orcamentos_cache_version()

# ── DADOS GLOBAIS ─────────────────────────────────────────────────────────────
df_reg  = cached_buscar_dados("SELECT * FROM formas_pagamento", version=orcamentos_cache_version)
lista_regras = df_reg.to_dict('records') if not df_reg.empty else []
emp_d = df_conf.iloc[0].to_dict() if not df_conf.empty else {}
kpi_df = cached_buscar_dados("""
    SELECT
        COUNT(*) AS total,
        COALESCE(SUM(CASE WHEN status = 'Aprovado' THEN 1 ELSE 0 END), 0) AS aprovados,
        COALESCE(SUM(CASE WHEN status = 'Pendente' THEN 1 ELSE 0 END), 0) AS pendentes
    FROM orcamentos
""", version=orcamentos_cache_version)

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("## 📋 Central de Orçamentos")

# KPIs de Negócio
if not kpi_df.empty:
    total_orc = int(kpi_df.iloc[0]['total'] or 0)
    aprov = int(kpi_df.iloc[0]['aprovados'] or 0)
    pend = int(kpi_df.iloc[0]['pendentes'] or 0)
    conv  = f"{aprov/total_orc*100:.0f}%" if total_orc else "0%"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("TOTAL", total_orc)
    k2.metric("APROVADOS", aprov)
    k3.metric("PENDENTES", pend)
    k4.metric("CONVERSÃO",       conv)

st.write("")

# ── FILTROS ───────────────────────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns([1, 1, 2])

# 1. Filtro de Status
filtro_status = col_f1.selectbox("Status", ["Todos","Pendente","Aprovado","Cancelado"], label_visibility="collapsed")

# 2. Filtro de Vendedor (Privacidade)
usuario_nome = st.session_state.get("usuario_nome", "Admin")
usuario_nivel = st.session_state.get("usuario_nivel", "VENDEDOR")

if usuario_nivel == "ADMIN":
    # Admin vê todos, mas pode filtrar um específico
    df_vendedores = cached_buscar_dados("SELECT nome FROM vendedores ORDER BY nome ASC", version=orcamentos_cache_version)
    lista_vendedores = ["Todos os Vendedores"] + df_vendedores['nome'].tolist() if not df_vendedores.empty else ["Todos os Vendedores"]
    filtro_vendedor = col_f2.selectbox("Vendedor", lista_vendedores, label_visibility="collapsed")
else:
    # Vendedor comum só vê o dele, sem opção de trocar
    filtro_vendedor = usuario_nome
    col_f2.markdown(f"<div style='padding:8px; background:rgba(255,255,255,0.05); border-radius:5px; text-align:center; font-size:0.8rem; color:#94a3b8;'>👤 {usuario_nome}</div>", unsafe_allow_html=True)

# 3. Busca de texto
busca = col_f3.text_input("🔍 Buscar cliente ou ID…", label_visibility="collapsed")

where_clauses = []
query_params = []

if filtro_status != "Todos":
    where_clauses.append("o.status = ?")
    query_params.append(filtro_status)

if usuario_nivel != "ADMIN":
    where_clauses.append("LOWER(o.vendedor) = LOWER(?)")
    query_params.append(usuario_nome)
elif filtro_vendedor != "Todos os Vendedores":
    where_clauses.append("o.vendedor = ?")
    query_params.append(filtro_vendedor)

busca = busca.strip()
if busca:
    busca_like = f"%{busca}%"
    where_clauses.append("(c.nome LIKE ? OR CAST(o.id AS TEXT) LIKE ?)")
    query_params.extend([busca_like, busca_like])

where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

filtro_state = (filtro_status, filtro_vendedor, usuario_nivel, usuario_nome, busca)
if st.session_state.get("hist_last_filters") != filtro_state:
    st.session_state["hist_last_filters"] = filtro_state
    st.session_state["hist_page"] = 1

st.write("")

# ── CARDS ─────────────────────────────────────────────────────────────────────
STATUS_COR = {"Aprovado": "#22c55e", "Pendente": "#f59e0b", "Cancelado": "#ef4444"}

count_df = cached_buscar_dados(
    f"""
    SELECT COUNT(*) AS total
    FROM orcamentos o
    LEFT JOIN clientes c ON o.cliente_id = c.id
    {where_sql}
    """,
    tuple(query_params),
    version=orcamentos_cache_version
)
total_resultados = int(count_df.iloc[0]['total']) if not count_df.empty else 0

if total_resultados > 0:
    if st.session_state.get("hist_page", 1) < 1:
        st.session_state["hist_page"] = 1

    ctl1, ctl2, ctl3 = st.columns([1, 1, 2])
    page_size = ctl1.selectbox("Itens por página", [10, 20, 50, 100], index=1, key="hist_page_size")
    total_paginas = max(1, (total_resultados + page_size - 1) // page_size)
    if st.session_state.get("hist_page", 1) > total_paginas:
        st.session_state["hist_page"] = total_paginas
    pagina_atual = ctl2.number_input("Página", min_value=1, max_value=total_paginas, step=1, key="hist_page")

    inicio = (pagina_atual - 1) * page_size
    fim = min(inicio + page_size, total_resultados)
    ctl3.caption(f"Exibindo {inicio + 1}-{fim} de {total_resultados} orçamento(s).")
    st.write("")

    df_view = cached_buscar_dados(
        f"""
        SELECT
            o.id,
            o.data,
            o.status,
            o.total,
            o.vendedor,
            o.validade_dias,
            o.obs_geral,
            o.itens_json,
            o.forma_pagamento,
            o.prazo_entrega,
            o.desconto_global,
            COALESCE(c.nome, 'Cliente N/A') AS cliente_nome,
            COALESCE(c.cnpj, 'N/A') AS cliente_cnpj,
            COALESCE(c.telefone, '') AS cliente_telefone
        FROM orcamentos o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        {where_sql}
        ORDER BY o.id DESC
        LIMIT ? OFFSET ?
        """,
        tuple(query_params + [int(page_size), int(inicio)]),
        version=orcamentos_cache_version
    )

    for _, row in df_view.iterrows():
        sid  = row['id']
        cli = {
            "nome": row.get('cliente_nome', 'Cliente N/A') or 'Cliente N/A',
            "cnpj": row.get('cliente_cnpj', 'N/A') or 'N/A',
            "telefone": row.get('cliente_telefone', '') or '',
        }
        pdf_cache = get_pdf_cache(row, cli)

        with st.container(border=True):
            # ── LINHA SUPERIOR: identificação + status + valor ────────────
            top_l, top_m, top_r = st.columns([3, 1.2, 1])

            with top_l:
                st.markdown(f"""
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
                        <code style="background:rgba(56,189,248,.12); color:#38bdf8;
                                     padding:3px 10px; border-radius:5px;
                                     font-size:.75rem; font-weight:700;">#{sid}</code>
                        <span style="font-size:1.15rem; font-weight:800;
                                     color:#f1f5f9;">{cli['nome']}</span>
                    </div>
                    <div style="color:#64748b; font-size:.78rem; line-height:1.8;">
                        📅 {row['data']} &nbsp;·&nbsp;
                        👤 {row['vendedor'].upper()} &nbsp;·&nbsp;
                        📄 {cli.get('cnpj','N/A')} &nbsp;·&nbsp;
                        📱 {cli.get('telefone','N/A')}
                    </div>
                """, unsafe_allow_html=True)

            with top_m:
                # Dropdown de status inline
                opts = ["Pendente", "Aprovado", "Cancelado"]
                new_st = st.selectbox(
                    "status", opts,
                    index=opts.index(row['status']) if row['status'] in opts else 0,
                    key=f"st_{sid}", label_visibility="collapsed"
                )
                if new_st != row['status']:
                    try:
                        executar_comando("UPDATE orcamentos SET status=? WHERE id=?",
                                         (new_st, sid))
                        bump_orcamentos_cache_version()
                        st.rerun()
                    except Exception as e:
                        log_ui_error(f"Falha ao atualizar status do orçamento {sid}", e)
                        st.error("Não foi possível atualizar o status do orçamento.")

            with top_r:
                st.markdown(
                    f"<p style='text-align:right; color:#22c55e; "
                    f"font-size:1.35rem; font-weight:900; margin:0; line-height:1.2;'>"
                    f"R$ {row['total']:,.2f}</p>"
                    f"<p style='text-align:right; color:#64748b; "
                    f"font-size:.7rem; margin:0;'>{row.get('prazo_entrega','N/A')}</p>",
                    unsafe_allow_html=True
                )

            # ── DIVISOR LEVE ───────────────────────────────────────────────
            st.markdown(
                "<hr style='margin:14px 0 12px; border:none; "
                "border-top:1px solid rgba(255,255,255,.05);'>",
                unsafe_allow_html=True
            )

            # ── LINHA INFERIOR: botões de ação ────────────────────────────
            b1, b2, b3, b4, b5, b6, b7 = st.columns([1, 1, 1, 1.4, 1, 1, 0.5])

            if b1.button("🔍 VER",    key=f"v_{sid}",  use_container_width=True):
                try:
                    obter_pdf_orcamento(row, cli, emp_d, lista_regras)
                    st.session_state[f"view_{sid}"] = True
                    st.rerun()
                except Exception as e:
                    log_ui_error(f"Falha ao gerar PDF para visualização do orçamento {sid}", e)
                    st.error("Não foi possível gerar o PDF para visualização.")

            if pdf_cache:
                b2.download_button(
                    "📥 PDF", pdf_cache["pdf_bytes"],
                    file_name=pdf_cache["file_name"],
                    key=f"dl_{sid}", use_container_width=True
                )
            elif b2.button("📄 Gerar PDF", key=f"prep_{sid}", use_container_width=True):
                try:
                    obter_pdf_orcamento(row, cli, emp_d, lista_regras)
                    st.rerun()
                except Exception as e:
                    log_ui_error(f"Falha ao preparar PDF do orçamento {sid}", e)
                    st.error("Não foi possível preparar o PDF deste orçamento.")

            # WhatsApp
            tw = "".join(filter(str.isdigit, str(cli.get('telefone',''))))
            lw = f"https://wa.me/55{tw}?text=Olá%20{cli['nome']}!%20Segue%20orçamento%20Ref%3A%20{sid}"
            b3.markdown(
                f'<a href="{lw}" target="_blank" style="text-decoration:none;">'
                f'<div style="background:rgba(37,211,102,.1); color:#25d366; '
                f'border:1px solid rgba(37,211,102,.3); border-radius:7px; '
                f'text-align:center; padding:7px 14px; font-size:.78rem; '
                f'font-weight:700; cursor:pointer; white-space:nowrap; '
                f'margin-top:4px;">WHATSAPP</div></a>',
                unsafe_allow_html=True
            )

            if b4.button("⚡ ENVIAR AUTO", key=f"api_{sid}",
                          type="primary", use_container_width=True):
                with st.spinner("Enviando…"):
                    try:
                        pdf_b = obter_pdf_orcamento(row, cli, emp_d, lista_regras)
                        p64 = base64.b64encode(pdf_b).decode()
                        r = requests.post(
                            "http://127.0.0.1:3000/send-pdf",
                            json={"number": f"55{tw}" if len(tw) <= 11 else tw,
                                  "pdf_base64": p64.replace("\n",""),
                                  "filename": f"Orc_{sid}.pdf",
                                  "caption": f"Orçamento Ref: {sid}"},
                            timeout=20
                        )
                        if r.status_code == 200:
                            st.success("Enviado!")
                        else:
                            st.error("Falha no envio automático.")
                    except Exception as e:
                        log_ui_error(f"Falha no envio automático do orçamento {sid}", e)
                        st.error("Motor offline ou envio indisponível.")

            if b5.button("📝 EDITAR", key=f"ed_{sid}", use_container_width=True):
                st.session_state.edit_mode = True
                st.session_state.orcamento_id_editar = sid
                st.switch_page("pages/3_2-Gerar_Orcamentos.py")

            if b6.button("👯 DUP",    key=f"dp_{sid}", use_container_width=True):
                st.session_state.edit_mode = False
                st.switch_page("pages/3_2-Gerar_Orcamentos.py")

            if b7.button("🗑️",        key=f"del_{sid}", use_container_width=True):
                st.session_state["confirm_delete_orc"] = sid
                st.rerun()

            if st.session_state.get("confirm_delete_orc") == sid:
                st.warning(f"Confirmar exclusão do orçamento #{sid}? Esta ação remove o registro e as fotos anexadas.")
                c_confirm, c_cancel = st.columns(2)
                if c_confirm.button("Confirmar Exclusão", key=f"confirm_del_{sid}", type="primary", use_container_width=True):
                    try:
                        executar_comando("DELETE FROM orcamentos WHERE id=?", (sid,))
                        limpar_fotos_orcamento(sid)
                        bump_orcamentos_cache_version()
                        st.session_state.get("orc_pdf_cache", {}).pop(str(sid), None)
                        st.session_state.pop("confirm_delete_orc", None)
                        st.success(f"Orçamento #{sid} excluído.")
                        st.rerun()
                    except Exception as e:
                        log_ui_error(f"Falha ao excluir orçamento {sid}", e)
                        st.error("Não foi possível excluir o orçamento.")
                if c_cancel.button("Cancelar", key=f"cancel_del_{sid}", use_container_width=True):
                    st.session_state.pop("confirm_delete_orc", None)
                    st.rerun()

            # ── VISUALIZAÇÃO DO PDF ───────────────────────────────────────
            if st.session_state.get(f"view_{sid}"):
                try:
                    pdf_b = obter_pdf_orcamento(row, cli, emp_d, lista_regras)
                    b64 = base64.b64encode(pdf_b).decode()
                    st.markdown(
                        f'<iframe src="data:application/pdf;base64,{b64}" '
                        f'width="100%" height="620" '
                        f'style="border:none; border-radius:10px; margin-top:16px; '
                        f'box-shadow:0 8px 30px rgba(0,0,0,.4);"></iframe>',
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    log_ui_error(f"Falha ao renderizar visualização do orçamento {sid}", e)
                    st.error("Não foi possível abrir a visualização do PDF.")
                if st.button("✕ Fechar", key=f"cv_{sid}"):
                    del st.session_state[f"view_{sid}"]; st.rerun()

        st.write("")   # respiro entre cards

else:
    st.info("💡 Nenhum orçamento encontrado.")
