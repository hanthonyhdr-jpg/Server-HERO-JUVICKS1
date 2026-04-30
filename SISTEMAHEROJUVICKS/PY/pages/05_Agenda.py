import streamlit as st
import os
import sys

# Adiciona a raiz do projeto ao sys.path para garantir que 'utils' e 'database' sejam encontrados
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import json
from database import buscar_dados, executar_comando, _log as db_log
from datetime import datetime, time
from utils.documentos import GeradorPDF
from utils.agenda_fotos import (
    carregar_lista_fotos,
    foto_para_bytes,
    normalizar_fotos_para_armazenar,
    remover_foto_da_lista,
    salvar_fotos_uploads,
)
from utils.query_cache import cached_buscar_dados, get_orcamentos_cache_version, bump_orcamentos_cache_version

# --- UTILS: Carregamento Seguro de JSON ---
def safe_loads(json_str, fallback=None):
    if fallback is None:
        fallback = []
    if not json_str or json_str == 'null':
        return fallback
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        st.warning(f"⚠️ Detectado dado corrompido em um registro. Algumas informações podem estar incompletas.")
        # Tenta uma recuperação básica se for um erro de truncamento comum
        try:
            # Se termina abruptamente, tenta fechar os colchetes/chaves.
            if json_str.startswith('[') and not json_str.endswith(']'):
                return json.loads(json_str + '"]')
        except json.JSONDecodeError:
            pass
        return fallback


def log_ui_error(contexto, erro):
    db_log(f"[AGENDA] {contexto}: {erro}")


def set_agenda_pending_action(action_type, row_id, **payload):
    st.session_state["agenda_pending_action"] = {
        "type": action_type,
        "row_id": int(row_id),
        **payload,
    }


def get_agenda_pending_action(row_id=None, action_type=None):
    action = st.session_state.get("agenda_pending_action")
    if not action:
        return None
    if row_id is not None and action.get("row_id") != int(row_id):
        return None
    if action_type is not None and action.get("type") != action_type:
        return None
    return action


def clear_agenda_pending_action():
    st.session_state.pop("agenda_pending_action", None)


DATA_SQL_EXPR = """
CASE
    WHEN o.data LIKE '__/__/____' THEN substr(o.data, 7, 4) || '-' || substr(o.data, 4, 2) || '-' || substr(o.data, 1, 2)
    WHEN o.data LIKE '____-__-__%' THEN substr(o.data, 1, 10)
    ELSE NULL
END
"""


def carregar_opcoes_select(sql, label_padrao, params=()):
    df_opts = cached_buscar_dados(sql, params, version=orcamentos_cache_version)
    if df_opts.empty:
        return [label_padrao]
    coluna = df_opts.columns[0]
    valores = sorted({str(valor).strip() for valor in df_opts[coluna].tolist() if pd.notna(valor) and str(valor).strip()})
    return [label_padrao] + valores


def montar_filtros_agenda(datas, sel_cidade, sel_bairro, sel_vendedor):
    where_clauses = []
    params = []

    if len(datas) == 2:
        start_date, end_date = datas
        where_clauses.append(f"{DATA_SQL_EXPR} BETWEEN ? AND ?")
        params.extend([start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])

    if sel_cidade != "Todas":
        where_clauses.append("c.cidade = ?")
        params.append(sel_cidade)

    if sel_bairro != "Todos":
        where_clauses.append("c.bairro = ?")
        params.append(sel_bairro)

    if sel_vendedor != "Todos":
        where_clauses.append("o.vendedor = ?")
        params.append(sel_vendedor)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    return where_sql, params


def montar_where_status(where_sql_base, status):
    return f"{where_sql_base} {'AND' if where_sql_base else 'WHERE'} o.status = ?"


def contar_agenda_status(where_sql_base, params_base):
    df_counts = cached_buscar_dados(
        f"""
        SELECT o.status, COUNT(*) AS total
        FROM orcamentos o
        JOIN clientes c ON o.cliente_id = c.id
        {where_sql_base}
        GROUP BY o.status
        """,
        tuple(params_base),
        version=orcamentos_cache_version
    )
    totais = {"Pendente": 0, "Aprovado": 0, "Cancelado": 0}
    for _, row in df_counts.iterrows():
        totais[str(row['status'])] = int(row['total'])
    return totais


def carregar_cards_agenda(where_sql_base, params_base, status, limit, offset):
    where_status = montar_where_status(where_sql_base, status)
    df_status = cached_buscar_dados(
        f"""
        SELECT
            o.id,
            o.data,
            {DATA_SQL_EXPR} AS data_norm,
            o.status,
            o.vendedor,
            o.itens_json,
            o.obs_geral,
            o.hora_agendamento,
            c.nome as cliente,
            c.cidade,
            c.bairro,
            c.cnpj as c_cnpj,
            c.telefone as c_tel,
            c.endereco as c_end,
            c.numero as c_num
        FROM orcamentos o
        JOIN clientes c ON o.cliente_id = c.id
        {where_status}
        ORDER BY data_norm DESC, o.id DESC
        LIMIT ? OFFSET ?
        """,
        tuple(list(params_base) + [status, int(limit), int(offset)]),
        version=orcamentos_cache_version
    )

    if not df_status.empty:
        df_status['data_original'] = df_status['data']
        df_status['data_dt'] = pd.to_datetime(df_status['data_norm'], errors='coerce')
    else:
        df_status['data_original'] = pd.Series(dtype='object')
        df_status['data_dt'] = pd.Series(dtype='datetime64[ns]')
    return df_status


def robust_parse_date(value):
    if value is None or value == "" or pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if isinstance(value, datetime):
        return value

    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue

    parsed = pd.to_datetime(value, errors='coerce', dayfirst=True)
    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime()


def robust_parse_time(value, default=None):
    default = default or time(8, 0)
    if isinstance(value, time):
        return value
    if value is None or value == "" or pd.isna(value):
        return default

    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return datetime.strptime(str(value), fmt).time()
        except ValueError:
            continue
    return default


def carregar_mapa_fotos(ids_orcamentos):
    ids_validos = [int(orc_id) for orc_id in ids_orcamentos if pd.notna(orc_id)]
    if not ids_validos:
        return {}

    placeholders = ",".join(["?"] * len(ids_validos))
    df_fotos = buscar_dados(
        f"""
        SELECT id, fotos_json
        FROM orcamentos
        WHERE id IN ({placeholders})
          AND fotos_json IS NOT NULL
          AND fotos_json NOT IN ('', '[]', 'null')
        """,
        tuple(ids_validos)
    )
    return {row['id']: carregar_lista_fotos(row['fotos_json']) for _, row in df_fotos.iterrows()}

from TEMAS.moderno import apply_modern_style
from utils.auth_manager import verificar_autenticacao, obter_dados_empresa, verificar_permissao_modulo

# --- 1. CONFIGURAÇÃO E DESIGN ---
df_conf = buscar_dados("SELECT * FROM config LIMIT 1")
nome_emp = df_conf.iloc[0]['empresa_nome'] if not df_conf.empty else "Sistema"
empresa_config = df_conf.iloc[0].to_dict() if not df_conf.empty else {"empresa_nome": nome_emp}

st.set_page_config(page_title=f"Agenda | {nome_emp}", layout="wide", page_icon="📅")

# Aplica o estilo global moderno com logo
_, logo_src = obter_dados_empresa()
apply_modern_style(logo_url=logo_src, nome_empresa=nome_emp)

# --- LOGIN PROTECTION ---
verificar_autenticacao()
from utils.auth_manager import verificar_nivel_acesso
verificar_nivel_acesso(["ADMIN", "GERENTE", "VENDEDOR", "INSTALADOR"])
verificar_permissao_modulo("Agenda")
orcamentos_cache_version = get_orcamentos_cache_version()

# --- 2. MANUTENÇÃO BANCO (Compatível com SQLite e PostgreSQL) ---
def init_db():
    try:
        # Busca apenas as colunas da tabela de forma universal
        df_tmp = buscar_dados("SELECT * FROM orcamentos WHERE 1=0")
        cols = df_tmp.columns.tolist()
        
        # Verifica e adiciona colunas se faltarem
        if "hora_agendamento" not in cols: 
            executar_comando("ALTER TABLE orcamentos ADD COLUMN hora_agendamento TEXT")
        if "fotos_json" not in cols: 
            executar_comando("ALTER TABLE orcamentos ADD COLUMN fotos_json TEXT")
            executar_comando("UPDATE orcamentos SET fotos_json = '[]' WHERE fotos_json IS NULL")
    except Exception as e:
        # Se a tabela ainda não existir, o próprio sistema de inicialização vai criar depois
        pass

init_db()

st.title("📅 Quadro de Operações & Agenda")
st.markdown("---")

# --- 4.5. FILTROS DA AGENDA ---
with st.expander("🔍 Filtros de Visualização Kanban", expanded=True):
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    # Período
    datas = col_f1.date_input("Período (Início - Fim)", value=[], key="filtro_periodo", format="DD/MM/YYYY")
    
    # Cidade
    cidades_disp = carregar_opcoes_select(
        """
        SELECT DISTINCT c.cidade
        FROM orcamentos o
        JOIN clientes c ON o.cliente_id = c.id
        WHERE c.cidade IS NOT NULL AND c.cidade <> ''
        ORDER BY c.cidade
        """,
        "Todas"
    )
    sel_cidade = col_f2.selectbox("Cidade", cidades_disp)
    
    # Bairro
    if sel_cidade != "Todas":
        bairros_disp = carregar_opcoes_select(
            """
            SELECT DISTINCT c.bairro
            FROM orcamentos o
            JOIN clientes c ON o.cliente_id = c.id
            WHERE c.cidade = ? AND c.bairro IS NOT NULL AND c.bairro <> ''
            ORDER BY c.bairro
            """,
            "Todos",
            (sel_cidade,)
        )
    else:
        bairros_disp = carregar_opcoes_select(
            """
            SELECT DISTINCT c.bairro
            FROM orcamentos o
            JOIN clientes c ON o.cliente_id = c.id
            WHERE c.bairro IS NOT NULL AND c.bairro <> ''
            ORDER BY c.bairro
            """,
            "Todos"
        )
    sel_bairro = col_f3.selectbox("Bairro", bairros_disp)
    
    # Vendedor
    vendedores_disp = carregar_opcoes_select(
        """
        SELECT DISTINCT o.vendedor
        FROM orcamentos o
        WHERE o.vendedor IS NOT NULL AND o.vendedor <> ''
        ORDER BY o.vendedor
        """,
        "Todos"
    )
    sel_vendedor = col_f4.selectbox("Consultor/Vendedor", vendedores_disp)

where_sql, query_params = montar_filtros_agenda(datas, sel_cidade, sel_bairro, sel_vendedor)

agenda_filter_state = (tuple(str(data) for data in datas), sel_cidade, sel_bairro, sel_vendedor)
if st.session_state.get("agenda_last_filters") != agenda_filter_state:
    st.session_state["agenda_last_filters"] = agenda_filter_state
    st.session_state["agenda_page_pendente"] = 1
    st.session_state["agenda_page_aprovado"] = 1
    st.session_state["agenda_page_cancelado"] = 1

totais_status = contar_agenda_status(where_sql, query_params)
cards_por_coluna = st.selectbox("Cards por coluna", [5, 10, 20, 50], index=1, key="agenda_page_size")
total_filtrado = sum(totais_status.values())

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Na Fila", totais_status["Pendente"])
m2.metric("Programados", totais_status["Aprovado"])
m3.metric("Cancelados", totais_status["Cancelado"])
m4.metric("Filtrados", total_filtrado)
m5.metric("Cards/Coluna", cards_por_coluna)

st.write("")

# --- 5. QUADRO KANBAN ---
c1, c2, c3 = st.columns(3)
workflow = [
    ("Pendente", c1, "🟡 FILA DE ESPERA", "#f1c40f"),
    ("Aprovado", c2, "🟢 PROGRAMADOS / EM EXECUÇÃO", "#2ecc71"),
    ("Cancelado", c3, "🔴 CANCELADOS / ARQUIVADOS", "#e74c3c")
]

for status, col, label, color in workflow:
    with col:
        total_status = totais_status.get(status, 0)
        status_key = status.lower()
        page_key = f"agenda_page_{status_key}"
        total_paginas = max(1, (total_status + cards_por_coluna - 1) // cards_por_coluna) if total_status else 1
        if st.session_state.get(page_key, 1) > total_paginas:
            st.session_state[page_key] = total_paginas
        pagina_atual = st.number_input(
            f"Página {status}",
            min_value=1,
            max_value=total_paginas,
            step=1,
            key=page_key,
            disabled=total_status == 0,
        )
        offset = (pagina_atual - 1) * cards_por_coluna
        df_status = carregar_cards_agenda(where_sql, query_params, status, cards_por_coluna, offset) if total_status else pd.DataFrame()
        fotos_por_orcamento = carregar_mapa_fotos(df_status['id'].tolist()) if status == "Aprovado" and not df_status.empty else {}

        st.markdown(f"""
            <div style='background-color: {color}22; padding: 10px; border-radius: 8px; border-left: 5px solid {color}; margin-bottom: 20px;'>
                <h4 style='margin: 0; color: {color};'>{label}</h4>
                <small style='color: #888;'>{total_status} registros</small>
            </div>
        """, unsafe_allow_html=True)
        if total_status:
            st.caption(f"Página {pagina_atual} de {total_paginas}")
        
        with st.expander(f"👁️ Exibir/Ocultar Fila", expanded=True):
            if df_status.empty:
                st.info("Nenhum item nesta coluna com os filtros atuais.")
            for _, row in df_status.iterrows():
                data_base = robust_parse_date(row.get('data_dt'))
                if data_base is None:
                    data_base = robust_parse_date(row.get('data_original'))
                data_formatada = data_base.strftime('%d/%m/%Y') if data_base else 'Sem data'
                header_label = f"👤 {row['cliente']} | 📅 {data_formatada}"
                
                with st.expander(header_label):
                    st.caption(f"ID: {row['id']} | 📍 {row.get('cidade', 'N/A')} - {row.get('bairro', 'N/A')}")
                    
                    # Detalhes do Serviço
                    st.markdown("---")
                    st.write("📋 **Itens do Pedido:**")
                    for item in safe_loads(row['itens_json']):
                        st.write(f"• {item.get('qtd', 1)}x {item.get('produto', 'Item Desconhecido')}")
                    
                    if status == "Aprovado":
                        st.divider()
                        st.write("⏰ **Programação e Campo:**")
                        cc1, cc2 = st.columns(2)
                        data_execucao = data_base.date() if data_base else datetime.now().date()
                        nova_d = cc1.date_input("Data de Execução", value=data_execucao, key=f"d{row['id']}", format="DD/MM/YYYY")

                        h_ini = robust_parse_time(row.get('hora_agendamento'))
                        nova_h = cc2.time_input("Horário", value=h_ini, key=f"h{row['id']}")
    
                        # Gestão de Fotos do Local
                        fotos_up = st.file_uploader("📸 Fotos da Obra/Local", accept_multiple_files=True, key=f"f{row['id']}")
                        
                        lista_f = fotos_por_orcamento.get(row['id'], []).copy()
                        
                        if lista_f:
                            st.write("🖼️ Fotos Anexadas:")
                            cols_img = st.columns(3)
                            for idx, img in enumerate(lista_f):
                                with cols_img[idx % 3]:
                                    img_bytes = foto_para_bytes(img)
                                    if img_bytes:
                                        st.image(img_bytes, use_container_width=True)
                                    if st.button("🗑️", key=f"del_{row['id']}_{idx}"):
                                        try:
                                            lista_f = remover_foto_da_lista(lista_f, idx)
                                            lista_f = normalizar_fotos_para_armazenar(lista_f, row['id'])
                                            executar_comando("UPDATE orcamentos SET fotos_json=? WHERE id=?", (json.dumps(lista_f), row['id']))
                                            bump_orcamentos_cache_version()
                                            st.rerun()
                                        except Exception as e:
                                            log_ui_error(f"Falha ao remover foto do orçamento {row['id']}", e)
                                            st.error("Não foi possível remover a foto anexada.")
                        
                        if st.button("💾 Atualizar Agenda", key=f"s{row['id']}", use_container_width=True, type="secondary"):
                            try:
                                lista_f = salvar_fotos_uploads(row['id'], fotos_up, lista_f)
                                lista_f = normalizar_fotos_para_armazenar(lista_f, row['id'])
                                executar_comando("UPDATE orcamentos SET data=?, hora_agendamento=?, fotos_json=? WHERE id=?", 
                                                 (nova_d.strftime('%Y-%m-%d'), nova_h.strftime('%H:%M'), json.dumps(lista_f), row['id']))
                                bump_orcamentos_cache_version()
                                st.success("Sincronizado!")
                                st.rerun()
                            except Exception as e:
                                log_ui_error(f"Falha ao atualizar agenda do orçamento {row['id']}", e)
                                st.error("Não foi possível atualizar a programação deste item.")
    
                        # Impressão Guia Técnico
                        st.write("")
                        if st.button("🖨️ Gerar Guia de Execução", key=f"p{row['id']}", type="primary", use_container_width=True):
                            try:
                                # Limpa observações financeiras
                                obs_limpa = str(row.get('obs_geral', '')).split("CONDIÇÕES DE PAGAMENTO:")[0].strip()
                                pdf = GeradorPDF.criar_guia_producao(
                                    id_orc=f"GUIA-{row['id']}", 
                                    empresa=empresa_config,
                                    cliente={"nome": row['cliente'], "cnpj": row['c_cnpj'], "telefone": row['c_tel'], "endereco": row['c_end'], "numero": row['c_num']},
                                    carrinho=safe_loads(row['itens_json']),
                                    obs_geral=obs_limpa,
                                    fotos=lista_f,
                                    data_obra=row.get('data'),
                                    hora_obra=row.get('hora_agendamento'),
                                    vendedor=row.get('vendedor', '')
                                )
                                st.download_button("⬇️ Baixar Guia PDF", data=pdf, file_name=f"GUIA_{row['id']}.pdf", use_container_width=True)
                            except Exception as e:
                                log_ui_error(f"Falha ao gerar guia do orçamento {row['id']}", e)
                                st.error("Não foi possível gerar a guia de execução.")
    
                    # Controle de Fluxo
                    st.divider()
                    st.write("🔄 **Mover para:**")
                    bt1, bt2 = st.columns(2)
                    if status != "Aprovado":
                        if bt1.button("✅ Aprovar/Agendar", key=f"ap{row['id']}", use_container_width=True):
                            set_agenda_pending_action("status_change", row['id'], new_status="Aprovado", label="aprovar e enviar para programação")
                            st.rerun()
                    if status != "Cancelado":
                        if bt2.button("🚫 Cancelar Item", key=f"cn{row['id']}", use_container_width=True):
                            set_agenda_pending_action("status_change", row['id'], new_status="Cancelado", label="cancelar este item")
                            st.rerun()
                    if status == "Cancelado" or status == "Aprovado":
                         if st.button("🔙 Voltar para Pendente", key=f"pe{row['id']}", use_container_width=True):
                             set_agenda_pending_action("status_change", row['id'], new_status="Pendente", label="retornar este item para a fila")
                             st.rerun()

                    pending_action = get_agenda_pending_action(row['id'], "status_change")
                    if pending_action:
                        st.warning(f"Confirmar ação: {pending_action['label']}?")
                        c_ok, c_no = st.columns(2)
                        if c_ok.button("Confirmar", key=f"confirm_status_{row['id']}", type="primary", use_container_width=True):
                            try:
                                executar_comando("UPDATE orcamentos SET status=? WHERE id=?", (pending_action['new_status'], row['id']))
                                bump_orcamentos_cache_version()
                                clear_agenda_pending_action()
                                st.success("Status atualizado.")
                                st.rerun()
                            except Exception as e:
                                log_ui_error(f"Falha ao atualizar status do orçamento {row['id']}", e)
                                st.error("Não foi possível alterar o status deste item.")
                        if c_no.button("Cancelar", key=f"cancel_status_{row['id']}", use_container_width=True):
                            clear_agenda_pending_action()
                            st.rerun()
