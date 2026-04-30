import streamlit as st
import pandas as pd
import json
from database import buscar_dados, executar_comando
from datetime import datetime, time
from utils.documentos import GeradorPDF
from utils.agenda_fotos import (
    carregar_lista_fotos,
    foto_para_bytes,
    normalizar_fotos_para_armazenar,
    remover_foto_da_lista,
    salvar_fotos_uploads,
)

# --- CONFIG E SEGURANÇA ---
df_conf = buscar_dados("SELECT * FROM config LIMIT 1")
nome_emp = df_conf.iloc[0]['empresa_nome'] if not df_conf.empty else "Sistema"
st.set_page_config(page_title=f"Agenda | {nome_emp}", layout="wide", page_icon="📅")

# --- MANUTENÇÃO BANCO ---
def init_db():
    cols = buscar_dados("PRAGMA table_info(orcamentos)")['name'].tolist()
    if "hora_agendamento" not in cols: 
        executar_comando("ALTER TABLE orcamentos ADD COLUMN hora_agendamento TEXT")
    if "fotos_json" not in cols: 
        executar_comando("ALTER TABLE orcamentos ADD COLUMN fotos_json TEXT")
init_db()

# --- BUSCA DE DADOS ---
df = buscar_dados('''
    SELECT o.*, c.nome as cliente, c.cnpj as c_cnpj, c.telefone as c_tel, c.endereco as c_end, c.numero as c_num
    FROM orcamentos o JOIN clientes c ON o.cliente_id = c.id
    ORDER BY o.data DESC
''')

st.title("📅 Agenda e Guia Técnico")

# Painel Kanban de Aprovados
for _, row in df[df['status'] == "Aprovado"].iterrows():
    with st.container(border=True):
        st.subheader(f"👤 {row['cliente']}")
        
        # Agendamento
        c_d, c_h = st.columns(2)
        def robust_parse_date(d_str):
            for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    return datetime.strptime(str(d_str), fmt)
                except:
                    continue
            return datetime.now()

        nova_d = c_d.date_input("Data do Serviço", value=robust_parse_date(row['data']), key=f"d{row['id']}")
        
        h_str = row['hora_agendamento'] if row['hora_agendamento'] else "08:00"
        h_val = datetime.strptime(h_str, '%H:%M').time()
        nova_h = c_h.time_input("Hora", value=h_val, key=f"h{row['id']}")

        # Upload de Fotos
        fotos_up = st.file_uploader("📸 Adicionar Fotos", accept_multiple_files=True, key=f"f{row['id']}")
        
        lista_f = carregar_lista_fotos(row['fotos_json'])
        
        if lista_f:
            st.write("🖼️ Galeria (Clique no X para remover):")
            cols_img = st.columns(4)
            for idx, img in enumerate(lista_f):
                with cols_img[idx % 4]:
                    img_bytes = foto_para_bytes(img)
                    if img_bytes:
                        st.image(img_bytes)
                    if st.button("❌", key=f"del_{row['id']}_{idx}"):
                        lista_f = remover_foto_da_lista(lista_f, idx)
                        lista_f = normalizar_fotos_para_armazenar(lista_f, row['id'])
                        executar_comando("UPDATE orcamentos SET fotos_json=? WHERE id=?", (json.dumps(lista_f), row['id']))
                        st.rerun()
        
        if st.button("💾 Salvar Dados", key=f"s{row['id']}", use_container_width=True):
            lista_f = salvar_fotos_uploads(row['id'], fotos_up, lista_f)
            lista_f = normalizar_fotos_para_armazenar(lista_f, row['id'])
            executar_comando("UPDATE orcamentos SET data=?, hora_agendamento=?, fotos_json=? WHERE id=?", 
                             (nova_d.strftime('%Y-%m-%d'), nova_h.strftime('%H:%M'), json.dumps(lista_f), row['id']))
            st.success("Salvo!"); st.rerun()

        # Botão de Impressão
        if st.button("🖨️ Imprimir Guia Técnica", key=f"p{row['id']}", type="primary", use_container_width=True):
            obs_limpa = str(row.get('obs_geral', '')).split("CONDIÇÕES DE PAGAMENTO:")[0].strip()
            pdf = GeradorPDF.criar_guia_producao(
                id_orc=f"GUIA-{row['id']}", 
                empresa=df_conf.iloc[0].to_dict(),
                cliente={"nome": row['cliente'], "cnpj": row['c_cnpj'], "telefone": row['c_tel'], "endereco": row['c_end'], "numero": row['c_num']},
                carrinho=json.loads(row['itens_json']),
                obs_geral=obs_limpa,
                fotos=lista_f,
                data_obra=row.get('data'),
                hora_obra=row.get('hora_agendamento'),
                vendedor=row.get('vendedor', '')
            )
            st.download_button("⬇️ Baixar Guia", data=pdf, file_name=f"GUIA_{row['id']}.pdf", use_container_width=True)
